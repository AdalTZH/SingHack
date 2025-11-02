"""
Predict Agent - Analyzes claims data to recommend the best insurance plan
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .database import DatabaseConnection, get_claims_by_destination, get_claims_by_claim_type, get_product_performance_stats
from .user_data_model import UserData
from .config import SCORING_WEIGHTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictAgent:
    """
    Predict Agent that analyzes historical claims data to recommend
    the best insurance plan for users based on their profile
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.product_scores = {}
    
    def analyze_claims_data(self, user_data: UserData) -> pd.DataFrame:
        """
        Analyze claims data based on user profile
        Returns a DataFrame with product analysis
        """
        self.db.connect()
        
        try:
            # Get all product performance stats
            query, params = get_product_performance_stats()
            all_products_df = pd.DataFrame(self.db.execute_query(query, params))
            
            # Filter and analyze based on user data
            relevant_claims = []
            
            # 1. Filter by destination
            dest_query, dest_params = get_claims_by_destination(user_data.travel_destination)
            dest_results = self.db.execute_query(dest_query, dest_params)
            if dest_results:
                dest_df = pd.DataFrame(dest_results)
                relevant_claims.append(('destination_match', dest_df))
            
            # 2. Analyze claim types relevant to user priorities
            claim_type_priority_map = {
                'medical': ['medical', 'hospital', 'emergency', 'treatment'],
                'trip_cancellation': ['cancellation', 'trip interruption', 'curtailment'],
                'baggage': ['baggage', 'luggage', 'personal effects', 'belongings'],
                'liability': ['liability', 'third party', 'legal']
            }
            
            for priority, claim_types in claim_type_priority_map.items():
                if getattr(user_data, f'priority_{priority}_coverage', False):
                    for ct in claim_types:
                        ct_query, ct_params = get_claims_by_claim_type(ct)
                        ct_results = self.db.execute_query(ct_query, ct_params)
                        if ct_results:
                            ct_df = pd.DataFrame(ct_results)
                            relevant_claims.append((f'{priority}_{ct}', ct_df))
            
            # Combine all relevant claims
            combined_analysis = self._combine_claims_analysis(all_products_df, relevant_claims, user_data)
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing claims data: {e}")
            return pd.DataFrame()
        finally:
            self.db.disconnect()
    
    def _combine_claims_analysis(self, all_products_df: pd.DataFrame, 
                                 relevant_claims: List, user_data: UserData) -> pd.DataFrame:
        """Combine and score products based on multiple factors"""
        
        if all_products_df.empty:
            return pd.DataFrame()
        
        # Start with base product statistics
        analysis_df = all_products_df.copy()
        
        # Calculate risk-adjusted scores (initialize as float)
        analysis_df['destination_match_score'] = 0.0
        analysis_df['claim_type_match_score'] = 0.0
        analysis_df['claim_frequency_score'] = 0.0
        analysis_df['claim_severity_score'] = 0.0
        analysis_df['processing_efficiency_score'] = 0.0
        
        # Score destination matches
        for label, claim_df in relevant_claims:
            if 'destination' in label and not claim_df.empty:
                for _, row in claim_df.iterrows():
                    product_name = row.get('product_name')
                    if product_name:
                        mask = analysis_df['product_name'] == product_name
                        if mask.any():
                            claim_count = float(row.get('claim_count', 0))
                            analysis_df.loc[mask, 'destination_match_score'] += claim_count
        
        # Score claim type matches
        priority_weights = {
            'medical': 1.5 if user_data.priority_medical_coverage else 0.5,
            'trip_cancellation': 1.5 if user_data.priority_trip_cancellation else 0.5,
            'baggage': 1.5 if user_data.priority_baggage_coverage else 0.5,
            'liability': 1.5 if user_data.priority_liability_coverage else 0.5
        }
        
        for label, claim_df in relevant_claims:
            if 'destination' not in label and not claim_df.empty:
                for priority in priority_weights.keys():
                    if priority in label:
                        weight = priority_weights[priority]
                        for _, row in claim_df.iterrows():
                            product_name = row.get('product_name')
                            if product_name:
                                mask = analysis_df['product_name'] == product_name
                                if mask.any():
                                    claim_count = float(row.get('claim_count', 0))
                                    current_value = float(analysis_df.loc[mask, 'claim_type_match_score'].iloc[0]) if mask.any() else 0.0
                                    analysis_df.loc[mask, 'claim_type_match_score'] = current_value + (claim_count * weight)
        
        # Normalize scores (0-100 scale)
        for col in ['destination_match_score', 'claim_type_match_score']:
            if analysis_df[col].max() > 0:
                max_val = float(analysis_df[col].max())
                analysis_df[col] = (analysis_df[col].astype(float) / max_val) * 100
        
        # Claim frequency score (lower is better for insurance companies, but we want products that handle claims well)
        # Higher total claims might indicate product is commonly used and trusted
        # Convert to float to handle Decimal types from database
        total_claims_max = float(analysis_df['total_claims'].max()) if not analysis_df.empty else 0
        if total_claims_max > 0:
            analysis_df['claim_frequency_score'] = (
                analysis_df['total_claims'].astype(float) / total_claims_max
            ) * 100
        
        # Claim severity score (lower avg claim amount is better for users - means less risky product)
        avg_claim_max = float(analysis_df['avg_claim_amount'].max()) if not analysis_df.empty else 0
        if avg_claim_max > 0:
            analysis_df['claim_severity_score'] = (
                100 - (analysis_df['avg_claim_amount'].astype(float) / avg_claim_max) * 100
            )
        
        # Processing efficiency (faster is better)
        if analysis_df['avg_processing_days'].notna().any():
            max_days = float(analysis_df['avg_processing_days'].max()) if not analysis_df.empty else 0
            if max_days > 0:
                analysis_df['processing_efficiency_score'] = (
                    (max_days - analysis_df['avg_processing_days'].fillna(max_days).astype(float)) / max_days
                ) * 100
        
        # Calculate composite score using configurable weights
        analysis_df['composite_score'] = (
            analysis_df['destination_match_score'] * SCORING_WEIGHTS['destination_match'] +
            analysis_df['claim_type_match_score'] * SCORING_WEIGHTS['claim_type_match'] +
            analysis_df['claim_frequency_score'] * SCORING_WEIGHTS['claim_frequency'] +
            analysis_df['claim_severity_score'] * SCORING_WEIGHTS['claim_severity'] +
            analysis_df['processing_efficiency_score'] * SCORING_WEIGHTS['processing_efficiency']
        )
        
        # Apply user-specific adjustments
        analysis_df = self._apply_user_adjustments(analysis_df, user_data)
        
        return analysis_df.sort_values('composite_score', ascending=False)
    
    def _apply_user_adjustments(self, df: pd.DataFrame, user_data: UserData) -> pd.DataFrame:
        """Apply user-specific adjustments to scores"""
        
        # Ensure composite_score is float type
        if 'composite_score' not in df.columns:
            df['composite_score'] = 0.0
        df['composite_score'] = df['composite_score'].astype(float)
        
        # Age-based adjustments (older travelers might prefer products with good medical coverage)
        if user_data.age > 60:
            # Boost products with higher medical claim handling
            claim_type_score = df.get('claim_type_match_score', pd.Series([0.0] * len(df)))
            df['composite_score'] = df['composite_score'] + claim_type_score.astype(float) * 0.1
        
        # Adventure activities adjustment
        if user_data.plans_adventure_activities:
            # Look for products that handle diverse claim types well
            claim_type_diversity = df.get('claim_type_diversity', pd.Series([0] * len(df)))
            diversity_max = float(claim_type_diversity.max()) if len(claim_type_diversity) > 0 and claim_type_diversity.max() > 0 else 0
            if diversity_max > 0:
                df['composite_score'] = df['composite_score'] + (claim_type_diversity.astype(float) / diversity_max * 20)
        
        # Trip duration adjustment (longer trips might need more comprehensive coverage)
        if user_data.trip_duration_days > 14:
            total_claims = df.get('total_claims', pd.Series([0] * len(df)))
            claims_max = float(total_claims.max()) if len(total_claims) > 0 and total_claims.max() > 0 else 0
            if claims_max > 0:
                df['composite_score'] = df['composite_score'] + (total_claims.astype(float) / claims_max * 10)
        
        return df
    
    def predict_best_plan(self, user_data: UserData, top_n: int = 3) -> List[Dict]:
        """
        Main prediction method - returns top N recommended insurance plans
        
        Args:
            user_data: UserData object with user profile
            top_n: Number of top recommendations to return
            
        Returns:
            List of dictionaries with recommendation details
        """
        logger.info(f"Predicting best plan for user: {user_data.travel_destination}")
        
        # Analyze claims data
        analysis_df = self.analyze_claims_data(user_data)
        
        if analysis_df.empty:
            logger.warning("No claims data available for analysis")
            return []
        
        # Get top N recommendations
        top_recommendations = []
        
        for idx, row in analysis_df.head(top_n).iterrows():
            recommendation = {
                'rank': len(top_recommendations) + 1,
                'product_name': row.get('product_name', 'Unknown'),
                'product_category': row.get('product_category', 'Unknown'),
                'composite_score': round(row.get('composite_score', 0), 2),
                'reasoning': self._generate_reasoning(row, user_data),
                'stats': {
                    'total_claims': int(row.get('total_claims', 0)),
                    'avg_claim_amount': round(float(row.get('avg_claim_amount', 0)), 2),
                    'unique_destinations': int(row.get('unique_destinations', 0)),
                    'avg_processing_days': round(float(row.get('avg_processing_days', 0)) if pd.notna(row.get('avg_processing_days')) else 0, 1),
                    'total_paid': round(float(row.get('total_paid', 0)), 2)
                },
                'match_scores': {
                    'destination_match': round(row.get('destination_match_score', 0), 2),
                    'claim_type_match': round(row.get('claim_type_match_score', 0), 2),
                    'claim_frequency': round(row.get('claim_frequency_score', 0), 2),
                    'claim_severity': round(row.get('claim_severity_score', 0), 2),
                    'processing_efficiency': round(row.get('processing_efficiency_score', 0), 2)
                }
            }
            top_recommendations.append(recommendation)
        
        return top_recommendations
    
    def _generate_reasoning(self, product_row: pd.Series, user_data: UserData) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        if product_row.get('destination_match_score', 0) > 50:
            reasons.append(f"Strong track record for claims in {user_data.travel_destination}")
        
        if product_row.get('claim_type_match_score', 0) > 50:
            reasons.append("Well-suited for your priority coverage needs")
        
        if product_row.get('avg_processing_days', 0) < 30 and product_row.get('avg_processing_days', 0) > 0:
            reasons.append("Fast claim processing times")
        
        if product_row.get('total_claims', 0) > 100:
            reasons.append("Extensive claims handling experience")
        
        if product_row.get('claim_type_diversity', 0) > 5:
            reasons.append("Comprehensive coverage for various claim types")
        
        if not reasons:
            reasons.append("Based on overall product performance metrics")
        
        return "; ".join(reasons)

