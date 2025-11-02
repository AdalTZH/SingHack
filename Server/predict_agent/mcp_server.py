"""
Predict Agent MCP Server
Exposes tools for insurance plan recommendations via Model Context Protocol

Tools provided:
- Find suitable insurance plans based on user data
- Analyze product performance statistics
- Get recommendations with detailed reasoning
"""
import sys
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastMCP
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    logger.error("FastMCP not available. Install with: pip install fastmcp")
    FASTMCP_AVAILABLE = False
    FastMCP = None

# Import predict agent components
from .api import PredictAgentAPI, get_insurance_recommendations
from .user_data_model import UserData
from .predict_agent import PredictAgent
from .database import DatabaseConnection, get_product_performance_stats

# Create MCP server instance
if FASTMCP_AVAILABLE:
    mcp_server = FastMCP(name="PredictAgentServer")
else:
    mcp_server = None

# ============================================================================
# IMPLEMENTATION FUNCTIONS
# ============================================================================

def _find_insurance_plans_impl(
    age: int,
    travel_destination: str,
    trip_duration_days: int,
    trip_type: Optional[str] = None,
    travel_style: Optional[str] = None,
    has_pre_existing_conditions: Optional[bool] = False,
    plans_adventure_activities: Optional[bool] = False,
    traveling_with_children: Optional[bool] = False,
    traveling_with_valuables: Optional[bool] = False,
    priority_medical_coverage: Optional[bool] = True,
    priority_trip_cancellation: Optional[bool] = False,
    priority_baggage_coverage: Optional[bool] = False,
    priority_liability_coverage: Optional[bool] = False,
    budget_range: Optional[str] = None,
    frequent_traveler: Optional[bool] = False,
    previous_claims: Optional[int] = 0,
    top_n: int = 3
) -> Dict:
    """Implementation for finding suitable insurance plans"""
    try:
        user_data_dict = {
            'age': age,
            'travel_destination': travel_destination,
            'trip_duration_days': trip_duration_days,
            'trip_type': trip_type,
            'travel_style': travel_style,
            'has_pre_existing_conditions': has_pre_existing_conditions,
            'plans_adventure_activities': plans_adventure_activities,
            'traveling_with_children': traveling_with_children,
            'traveling_with_valuables': traveling_with_valuables,
            'priority_medical_coverage': priority_medical_coverage,
            'priority_trip_cancellation': priority_trip_cancellation,
            'priority_baggage_coverage': priority_baggage_coverage,
            'priority_liability_coverage': priority_liability_coverage,
            'budget_range': budget_range,
            'frequent_traveler': frequent_traveler,
            'previous_claims': previous_claims
        }
        
        # Get recommendations using the API
        result = get_insurance_recommendations(user_data_dict, top_n=top_n)
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding insurance plans: {e}")
        return {
            'success': False,
            'error': str(e),
            'recommendations': []
        }


def _get_product_statistics_impl(product_name: Optional[str] = None, limit: int = 10) -> Dict:
    """Implementation for getting product performance statistics"""
    try:
        db = DatabaseConnection()
        db.connect()
        
        try:
            # Get product performance stats
            query, params = get_product_performance_stats()
            results = db.execute_query(query, params)
            
            if not results:
                return {'products': [], 'total': 0}
            
            products = []
            for row in results:
                product = {
                    'product_name': row.get('product_name', 'Unknown'),
                    'product_category': row.get('product_category', 'Unknown'),
                    'total_claims': int(row.get('total_claims', 0)),
                    'unique_destinations': int(row.get('unique_destinations', 0)),
                    'avg_claim_amount': float(row.get('avg_claim_amount', 0)),
                    'total_claim_amount': float(row.get('total_claim_amount', 0)),
                    'total_paid': float(row.get('total_paid', 0)),
                    'claim_type_diversity': int(row.get('claim_type_diversity', 0)),
                    'avg_processing_days': float(row.get('avg_processing_days', 0)) if row.get('avg_processing_days') else None
                }
                
                # Filter by product name if specified
                if product_name:
                    if product_name.lower() in product['product_name'].lower():
                        products.append(product)
                else:
                    products.append(product)
            
            # Limit results
            if limit > 0:
                products = products[:limit]
            
            return {
                'products': products,
                'total': len(products),
                'filtered_by': product_name if product_name else 'all'
            }
            
        finally:
            db.disconnect()
            
    except Exception as e:
        logger.error(f"Error getting product statistics: {e}")
        return {'products': [], 'total': 0, 'error': str(e)}


def _analyze_destination_coverage_impl(destination: str) -> Dict:
    """Implementation for analyzing insurance coverage for a specific destination"""
    try:
        from .database import get_claims_by_destination
        
        db = DatabaseConnection()
        db.connect()
        
        try:
            # Get claims data for destination
            query, params = get_claims_by_destination(destination)
            results = db.execute_query(query, params)
            
            if not results:
                return {
                    'destination': destination,
                    'products': [],
                    'total_claims': 0,
                    'message': f'No claims data found for {destination}'
                }
            
            # Aggregate by product
            product_stats = {}
            for row in results:
                product_name = row.get('product_name', 'Unknown')
                if product_name not in product_stats:
                    product_stats[product_name] = {
                        'product_name': product_name,
                        'product_category': row.get('product_category', 'Unknown'),
                        'total_claims': 0,
                        'avg_claim_amount': 0,
                        'claim_types': set(),
                        'closed_claims': 0,
                        'open_claims': 0
                    }
                
                product_stats[product_name]['total_claims'] += row.get('claim_count', 0)
                product_stats[product_name]['claim_types'].add(row.get('claim_type', 'Unknown'))
                product_stats[product_name]['closed_claims'] += row.get('closed_claims', 0)
                product_stats[product_name]['open_claims'] += row.get('open_claims', 0)
            
            # Convert to list and calculate averages
            products = []
            for product_name, stats in product_stats.items():
                stats['claim_types'] = list(stats['claim_types'])
                products.append(stats)
            
            # Sort by total claims
            products.sort(key=lambda x: x['total_claims'], reverse=True)
            
            return {
                'destination': destination,
                'products': products,
                'total_products': len(products),
                'total_claims': sum(p['total_claims'] for p in products)
            }
            
        finally:
            db.disconnect()
            
    except Exception as e:
        logger.error(f"Error analyzing destination coverage: {e}")
        return {'destination': destination, 'products': [], 'error': str(e)}


# ============================================================================
# REGISTER MCP TOOLS
# ============================================================================

if mcp_server:
    @mcp_server.tool(
        name="find_insurance_plans",
        description="Find suitable insurance plans based on user data. Analyzes historical claims data to recommend the best insurance products matching the user's profile, destination, and coverage priorities. Returns top N recommendations with scores and reasoning."
    )
    def find_insurance_plans(
        age: int,
        travel_destination: str,
        trip_duration_days: int,
        trip_type: Optional[str] = None,
        travel_style: Optional[str] = None,
        has_pre_existing_conditions: Optional[bool] = False,
        plans_adventure_activities: Optional[bool] = False,
        traveling_with_children: Optional[bool] = False,
        traveling_with_valuables: Optional[bool] = False,
        priority_medical_coverage: Optional[bool] = True,
        priority_trip_cancellation: Optional[bool] = False,
        priority_baggage_coverage: Optional[bool] = False,
        priority_liability_coverage: Optional[bool] = False,
        budget_range: Optional[str] = None,
        frequent_traveler: Optional[bool] = False,
        previous_claims: Optional[int] = 0,
        top_n: int = 3
    ) -> Dict:
        """Find suitable insurance plans for a user"""
        return _find_insurance_plans_impl(
            age, travel_destination, trip_duration_days,
            trip_type, travel_style,
            has_pre_existing_conditions, plans_adventure_activities,
            traveling_with_children, traveling_with_valuables,
            priority_medical_coverage, priority_trip_cancellation,
            priority_baggage_coverage, priority_liability_coverage,
            budget_range, frequent_traveler, previous_claims, top_n
        )
    
    @mcp_server.tool(
        name="get_product_statistics",
        description="Get performance statistics for insurance products. Returns aggregated data including total claims, average claim amounts, processing times, and coverage diversity for products in the database."
    )
    def get_product_statistics(
        product_name: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """Get product performance statistics"""
        return _get_product_statistics_impl(product_name, limit)
    
    @mcp_server.tool(
        name="analyze_destination_coverage",
        description="Analyze insurance product coverage and claims data for a specific travel destination. Returns which products have the most claims handling experience for that destination, claim types covered, and product performance metrics."
    )
    def analyze_destination_coverage(
        destination: str
    ) -> Dict:
        """Analyze coverage for a specific destination"""
        return _analyze_destination_coverage_impl(destination)
    
    logger.info("MCP server tools registered successfully")
else:
    logger.warning("MCP server not available - tools cannot be registered")


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    if mcp_server:
        # Run the MCP server
        # FastMCP uses stdio transport for MCP protocol by default
        try:
            mcp_server.run()
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            sys.exit(1)
    else:
        print("Error: FastMCP not available. Install with: pip install fastmcp")
        sys.exit(1)

