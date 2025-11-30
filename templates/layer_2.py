"""
Travel Insurance Benefit Search & Scoring System
Layer 2 Benefits Only - Focused Benefit Queries
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Result structure for benefit searches"""
    success: bool
    data: Any
    message: str = ""


class BenefitSearchEngine:
    """
    Specialized engine for Layer 2 benefit searching and product scoring
    """

    def __init__(self, json_file_path: str):
        """Load the insurance data"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.products = self.data.get('products', [])
        self.benefits = self.data['layers']['layer_2_benefits']

        # Build lookup indexes
        self._build_indexes()
        
        print(f"✓ Loaded {len(self.products)} products")
        print(f"✓ Loaded {len(self.benefits)} Layer 2 benefits")

    def _build_indexes(self):
        """Build quick lookup indexes"""
        # Benefit name -> benefit data
        self.benefit_map = {b['benefit_name']: b for b in self.benefits}
        
        # Product -> list of benefits with details
        self.product_benefits_map = {}
        for product in self.products:
            self.product_benefits_map[product] = []
            for benefit in self.benefits:
                if benefit['products'].get(product, {}).get('condition_exist', False):
                    self.product_benefits_map[product].append({
                        'benefit_name': benefit['benefit_name'],
                        'parameters': benefit['products'][product].get('parameters', {})
                    })

    # ==================== BENEFIT SEARCH FUNCTIONS ====================

    def search_benefits_by_keyword(self, keyword: str) -> SearchResult:
        """
        Search for benefits containing a keyword
        
        Example:
            search_benefits_by_keyword("medical")
            search_benefits_by_keyword("luggage")
            search_benefits_by_keyword("delay")
        """
        keyword_lower = keyword.lower()
        matching_benefits = []
        
        for benefit_name, benefit_data in self.benefit_map.items():
            if keyword_lower in benefit_name.lower():
                # Get product availability
                available_products = [
                    p for p in self.products
                    if benefit_data['products'].get(p, {}).get('condition_exist', False)
                ]
                
                matching_benefits.append({
                    'benefit_name': benefit_name,
                    'available_in': available_products,
                    'product_count': len(available_products)
                })
        
        # Sort by availability (most available first)
        matching_benefits.sort(key=lambda x: x['product_count'], reverse=True)
        
        return SearchResult(
            success=len(matching_benefits) > 0,
            data={
                'keyword': keyword,
                'total_matches': len(matching_benefits),
                'benefits': matching_benefits
            },
            message=f"Found {len(matching_benefits)} benefits matching '{keyword}'"
        )

    def get_benefit_details(self, benefit_name: str, product_name: str) -> SearchResult:
        """
        Get detailed information about a specific benefit for a product
        
        Example:
            get_benefit_details("overseas_medical_expenses", "Scootsurance")
            get_benefit_details("trip_cancellation", "Income")
        """
        if benefit_name not in self.benefit_map:
            return SearchResult(
                success=False,
                data=None,
                message=f"Benefit '{benefit_name}' not found"
            )
        
        benefit_data = self.benefit_map[benefit_name]
        product_benefit = benefit_data['products'].get(product_name, {})
        
        if not product_benefit.get('condition_exist', False):
            return SearchResult(
                success=False,
                data=None,
                message=f"'{product_name}' does not offer '{benefit_name}'"
            )
        
        # Extract benefit details
        details = {
            'benefit_name': benefit_name,
            'product': product_name,
            'offered': True,
            'parameters': product_benefit.get('parameters', {}),
            'original_text': product_benefit.get('original_text', 'N/A')
        }
        
        return SearchResult(
            success=True,
            data=details,
            message=f"Benefit details retrieved for '{benefit_name}' in '{product_name}'"
        )

    def list_all_benefits_for_product(self, product_name: str) -> SearchResult:
        """
        List all benefits offered by a specific product
        
        Example:
            list_all_benefits_for_product("Scootsurance")
            list_all_benefits_for_product("Income")
        """
        if product_name not in self.products:
            return SearchResult(
                success=False,
                data=None,
                message=f"Product '{product_name}' not found"
            )
        
        benefits_list = self.product_benefits_map.get(product_name, [])
        
        return SearchResult(
            success=True,
            data={
                'product': product_name,
                'total_benefits': len(benefits_list),
                'benefits': benefits_list
            },
            message=f"Found {len(benefits_list)} benefits for '{product_name}'"
        )

    def compare_benefit_across_products(self, benefit_name: str) -> SearchResult:
        """
        Compare how different products cover a specific benefit
        
        Example:
            compare_benefit_across_products("overseas_medical_expenses")
            compare_benefit_across_products("personal_accident")
        """
        if benefit_name not in self.benefit_map:
            return SearchResult(
                success=False,
                data=None,
                message=f"Benefit '{benefit_name}' not found"
            )
        
        benefit_data = self.benefit_map[benefit_name]
        comparison = {
            'benefit_name': benefit_name,
            'products': {}
        }
        
        for product in self.products:
            product_benefit = benefit_data['products'].get(product, {})
            
            if product_benefit.get('condition_exist', False):
                comparison['products'][product] = {
                    'offered': True,
                    'parameters': product_benefit.get('parameters', {}),
                    'coverage_details': self._extract_key_parameters(
                        product_benefit.get('parameters', {})
                    )
                }
            else:
                comparison['products'][product] = {
                    'offered': False,
                    'parameters': {},
                    'coverage_details': 'Not offered'
                }
        
        return SearchResult(
            success=True,
            data=comparison,
            message=f"Comparison completed for '{benefit_name}'"
        )

    def _extract_key_parameters(self, parameters: Dict) -> str:
        """Extract human-readable key parameters"""
        if not parameters:
            return "Standard coverage"
        
        key_info = []
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                key_info.append(f"{key}: ${value:,}" if value > 1000 else f"{key}: {value}")
            else:
                key_info.append(f"{key}: {value}")
        
        return " | ".join(key_info) if key_info else "Standard coverage"

    def get_all_available_benefits(self) -> SearchResult:
        """
        Get a list of all available benefits across all products
        
        Example:
            get_all_available_benefits()
        """
        all_benefits = []
        
        for benefit_name, benefit_data in self.benefit_map.items():
            available_products = [
                p for p in self.products
                if benefit_data['products'].get(p, {}).get('condition_exist', False)
            ]
            
            all_benefits.append({
                'benefit_name': benefit_name,
                'available_in_products': available_products,
                'coverage_count': len(available_products)
            })
        
        # Sort by coverage count
        all_benefits.sort(key=lambda x: x['coverage_count'], reverse=True)
        
        return SearchResult(
            success=True,
            data={
                'total_benefits': len(all_benefits),
                'benefits': all_benefits
            },
            message=f"Retrieved {len(all_benefits)} total benefits"
        )

    # ==================== SCORING SYSTEM ====================

    # Preset benefit weights based on common importance
    PRESET_WEIGHTS = {
        # Medical - Highest priority
        "overseas_medical_expenses": 3.0,
        "emergency_medical_evacuation": 2.5,
        "hospital_allowance": 1.5,
        
        # Personal Safety - High priority
        "accidental_death_permanent_disablement": 2.5,
        "personal_accident": 2.5,
        
        # Trip Protection - Medium-High priority
        "trip_cancellation": 2.0,
        "trip_postponement": 2.0,
        "trip_curtailment": 1.8,
        "missed_departure": 1.5,
        
        # Belongings - Medium priority
        "baggage_loss": 1.8,
        "baggage_delay": 1.5,
        "personal_belongings": 1.5,
        "personal_money": 1.3,
        
        # Travel Inconvenience - Lower priority
        "travel_delay": 1.2,
        "flight_delay": 1.2,
        "flight_diversion": 1.0,
        
        # Other - Standard priority
        "travel_document_loss": 1.0,
        "personal_liability": 1.5,
        "rental_vehicle_excess": 1.0,
    }

    def score_products_by_benefits(self, priority_benefits: List[str], 
                                   weights: Optional[Dict[str, float]] = None,
                                   use_preset_weights: bool = True) -> SearchResult:
        """
        Score and rank products based on desired benefits with preset weights
        
        Example:
            # Use preset weights (default)
            score_products_by_benefits([
                "overseas_medical_expenses",
                "trip_cancellation",
                "baggage_delay"
            ])
            
            # Override with custom weights
            score_products_by_benefits(
                ["overseas_medical_expenses", "trip_cancellation"],
                weights={"overseas_medical_expenses": 5.0, "trip_cancellation": 3.0},
                use_preset_weights=False
            )
            
            # Mix preset and custom weights
            score_products_by_benefits(
                ["overseas_medical_expenses", "trip_cancellation", "custom_benefit"],
                weights={"custom_benefit": 2.0}  # Preset weights used for others
            )
        """
        if not priority_benefits:
            return SearchResult(
                success=False,
                data=None,
                message="No priority benefits provided"
            )
        
        # Build weights dictionary
        if use_preset_weights:
            # Start with preset weights
            final_weights = {}
            for benefit in priority_benefits:
                final_weights[benefit] = self.PRESET_WEIGHTS.get(benefit, 1.0)
            
            # Override with custom weights if provided
            if weights:
                final_weights.update(weights)
        else:
            # Use only custom weights or default to 1.0
            if weights is None:
                final_weights = {benefit: 1.0 for benefit in priority_benefits}
            else:
                final_weights = weights
        
        scores = []
        
        for product in self.products:
            score = 0
            covered_benefits = []
            missing_benefits = []
            coverage_details = []
            weighted_breakdown = []
            
            for benefit in priority_benefits:
                weight = final_weights.get(benefit, 1.0)
                
                if benefit not in self.benefit_map:
                    continue
                
                benefit_data = self.benefit_map[benefit]
                product_benefit = benefit_data['products'].get(product, {})
                
                if product_benefit.get('condition_exist', False):
                    benefit_score = 10 * weight
                    score += benefit_score
                    covered_benefits.append(benefit)
                    
                    weighted_breakdown.append({
                        'benefit': benefit,
                        'weight': weight,
                        'score_contribution': benefit_score
                    })
                    
                    # Extract coverage amount for ranking
                    params = product_benefit.get('parameters', {})
                    coverage_details.append({
                        'benefit': benefit,
                        'parameters': params
                    })
                else:
                    missing_benefits.append(benefit)
            
            # Bonus: total benefit count
            total_benefits = len(self.product_benefits_map.get(product, []))
            bonus_score = total_benefits * 0.5
            score += bonus_score
            
            scores.append({
                'product': product,
                'score': round(score, 2),
                'covered_priority_benefits': covered_benefits,
                'missing_priority_benefits': missing_benefits,
                'coverage_match_percentage': round(
                    (len(covered_benefits) / len(priority_benefits)) * 100, 1
                ),
                'total_benefits_offered': total_benefits,
                'weighted_breakdown': weighted_breakdown,
                'bonus_score': round(bonus_score, 2),
                'coverage_details': coverage_details
            })
        
        # Sort by score
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        return SearchResult(
            success=True,
            data={
                'priority_benefits': priority_benefits,
                'rankings': scores,
                'recommended_product': scores[0]['product'] if scores else None,
                'top_score': scores[0]['score'] if scores else 0
            },
            message=f"Ranked {len(scores)} products"
        )

    def recommend_product(self, must_have_benefits: List[str], 
                         nice_to_have_benefits: Optional[List[str]] = None) -> SearchResult:
        """
        Recommend products with must-have and nice-to-have benefits
        
        Example:
            recommend_product(
                must_have_benefits=["overseas_medical_expenses"],
                nice_to_have_benefits=["trip_cancellation", "baggage_delay"]
            )
        """
        if not must_have_benefits:
            return SearchResult(
                success=False,
                data=None,
                message="Must provide at least one must-have benefit"
            )
        
        nice_to_have_benefits = nice_to_have_benefits or []
        recommendations = []
        
        for product in self.products:
            # Check must-have benefits
            must_have_covered = []
            must_have_missing = []
            
            for benefit in must_have_benefits:
                if benefit not in self.benefit_map:
                    continue
                
                benefit_data = self.benefit_map[benefit]
                product_benefit = benefit_data['products'].get(product, {})
                
                if product_benefit.get('condition_exist', False):
                    must_have_covered.append(benefit)
                else:
                    must_have_missing.append(benefit)
            
            # Skip if missing any must-have benefits
            if must_have_missing:
                continue
            
            # Check nice-to-have benefits
            nice_to_have_covered = []
            nice_to_have_missing = []
            
            for benefit in nice_to_have_benefits:
                if benefit not in self.benefit_map:
                    continue
                
                benefit_data = self.benefit_map[benefit]
                product_benefit = benefit_data['products'].get(product, {})
                
                if product_benefit.get('condition_exist', False):
                    nice_to_have_covered.append(benefit)
                else:
                    nice_to_have_missing.append(benefit)
            
            # Calculate score
            score = len(must_have_covered) * 10 + len(nice_to_have_covered) * 5
            total_benefits = len(self.product_benefits_map.get(product, []))
            score += total_benefits * 0.3
            
            recommendations.append({
                'product': product,
                'score': round(score, 2),
                'must_have_covered': must_have_covered,
                'nice_to_have_covered': nice_to_have_covered,
                'nice_to_have_missing': nice_to_have_missing,
                'total_benefits': total_benefits
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        if not recommendations:
            return SearchResult(
                success=False,
                data=None,
                message="No products meet all must-have requirements"
            )
        
        return SearchResult(
            success=True,
            data={
                'must_have_benefits': must_have_benefits,
                'nice_to_have_benefits': nice_to_have_benefits,
                'recommended_product': recommendations[0]['product'],
                'recommendations': recommendations
            },
            message=f"Found {len(recommendations)} qualifying products"
        )


# ==================== USAGE EXAMPLES ====================

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print('='*70)


def example_search_benefits(engine: BenefitSearchEngine, keyword: str):
    """Example: Search benefits by keyword"""
    print_header(f"Search Benefits: '{keyword}'")
    
    result = engine.search_benefits_by_keyword(keyword)
    if result.success:
        print(f"✓ {result.message}\n")
        for benefit in result.data['benefits']:
            print(f"  • {benefit['benefit_name']}")
            print(f"    Available in: {', '.join(benefit['available_in'])}")
            print(f"    ({benefit['product_count']} products)\n")
    else:
        print(f"✗ {result.message}")


def example_get_benefit_details(engine: BenefitSearchEngine, benefit: str, product: str):
    """Example: Get specific benefit details"""
    print_header(f"Benefit Details: {benefit} ({product})")
    
    result = engine.get_benefit_details(benefit, product)
    if result.success:
        print(f"✓ {result.message}\n")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"✗ {result.message}")


def example_list_benefits(engine: BenefitSearchEngine, product: str):
    """Example: List all benefits for a product"""
    print_header(f"All Benefits for: {product}")
    
    result = engine.list_all_benefits_for_product(product)
    if result.success:
        print(f"✓ {result.message}\n")
        for i, benefit in enumerate(result.data['benefits'], 1):
            print(f"{i}. {benefit['benefit_name']}")
            if benefit['parameters']:
                print(f"   Parameters: {json.dumps(benefit['parameters'], indent=3)}")
            print()
    else:
        print(f"✗ {result.message}")


def example_compare_benefit(engine: BenefitSearchEngine, benefit: str):
    """Example: Compare benefit across products"""
    print_header(f"Compare: {benefit}")
    
    result = engine.compare_benefit_across_products(benefit)
    if result.success:
        print(f"✓ {result.message}\n")
        for product, details in result.data['products'].items():
            print(f"  {product}:")
            if details['offered']:
                print(f"    ✓ Offered")
                print(f"    Details: {details['coverage_details']}")
            else:
                print(f"    ✗ Not offered")
            print()
    else:
        print(f"✗ {result.message}")


def example_score_products(engine: BenefitSearchEngine, benefits: List[str]):
    """Example: Score products by benefits"""
    print_header(f"Product Scoring with Preset Weights")
    print(f"Priority Benefits: {', '.join(benefits)}\n")
    
    result = engine.score_products_by_benefits(benefits)
    if result.success:
        print(f"✓ {result.message}\n")
        print(f"Weights Used:")
        for benefit, weight in result.data['weights_used'].items():
            print(f"  • {benefit}: {weight}x")
        print(f"\n🏆 Recommended: {result.data['recommended_product']} (Score: {result.data['top_score']})\n")
        print("Rankings:\n")
        for i, ranking in enumerate(result.data['rankings'], 1):
            print(f"{i}. {ranking['product']} - Total Score: {ranking['score']}")
            print(f"   Covered: {ranking['covered_priority_benefits']}")
            print(f"   Missing: {ranking['missing_priority_benefits']}")
            print(f"   Match: {ranking['coverage_match_percentage']}%")
            if ranking.get('weighted_breakdown'):
                print(f"   Score Breakdown:")
                for item in ranking['weighted_breakdown']:
                    print(f"     - {item['benefit']}: {item['score_contribution']} pts (weight: {item['weight']}x)")
                print(f"     - Bonus (total benefits): {ranking['bonus_score']} pts")
            print(f"   Total Benefits: {ranking['total_benefits_offered']}\n")
    else:
        print(f"✗ {result.message}")


def example_recommend(engine: BenefitSearchEngine, must_have: List[str], nice_to_have: List[str]):
    """Example: Recommend products"""
    print_header(f"Product Recommendation")
    print(f"Must Have: {', '.join(must_have)}")
    print(f"Nice to Have: {', '.join(nice_to_have)}\n")
    
    result = engine.recommend_product(must_have, nice_to_have)
    if result.success:
        print(f"✓ {result.message}\n")
        print(f"🏆 Recommended: {result.data['recommended_product']}\n")
        print("All Qualified Products:\n")
        for rec in result.data['recommendations']:
            print(f"  • {rec['product']} (Score: {rec['score']})")
            print(f"    Nice-to-have covered: {rec['nice_to_have_covered']}")
            print(f"    Total benefits: {rec['total_benefits']}\n")
    else:
        print(f"✗ {result.message}")


if __name__ == "__main__":
    # Initialize the engine
    FILE_PATH = './Server/Taxonomy_Hackathon.json'
    
    print_header("INITIALIZING BENEFIT SEARCH ENGINE")
    engine = BenefitSearchEngine(FILE_PATH)
    print(f"\nAvailable products: {', '.join(engine.products)}\n")
    
    # Example 1: Search benefits by keyword
    example_search_benefits(engine, "medical")
    
    # Example 2: Get specific benefit details
    example_get_benefit_details(
        engine, 
        "overseas_medical_expenses", 
        engine.products[0]
    )
    
    # Example 3: List all benefits for a product
    example_list_benefits(engine, engine.products[0])
    
    # Example 4: Compare benefit across products
    example_compare_benefit(engine, "overseas_medical_expenses")
    
    # Example 5: Score products
    priority_benefits = [
        "overseas_medical_expenses",
        "trip_cancellation",
        "personal_accident"
    ]
    example_score_products(engine, priority_benefits)
    
    # Example 6: Recommend products
    example_recommend(
        engine,
        must_have=["overseas_medical_expenses"],
        nice_to_have=["trip_cancellation", "baggage_delay"]
    )