"""
Efficient Query System for Pre-Indexed Travel Insurance JSON
Optimized for the existing JSON structure with built-in indexing
"""

import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class QueryResult:
    """Standardized query result structure"""
    success: bool
    data: Any
    message: str = ""


class TravelInsuranceQuery:
    """
    Query engine for pre-indexed travel insurance JSON data
    Provides fast lookups and comparisons without rebuilding indexes
    """

    def __init__(self, json_file_path: str):
        """Load the pre-indexed JSON file"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.products = self.data.get('products', [])
        self.layer1 = self.data['layers']['layer_1_general_conditions']
        self.layer2 = self.data['layers']['layer_2_benefits']
        self.layer3 = self.data['layers'][
            'layer_3_benefit_specific_conditions']

        # Build quick lookup maps for O(1) access
        self._build_quick_lookups()

        print(f"✓ Loaded {len(self.products)} products")
        print(f"✓ Layer 1: {len(self.layer1)} general conditions")
        print(f"✓ Layer 2: {len(self.layer2)} benefits")
        print(f"✓ Layer 3: {len(self.layer3)} benefit-specific conditions")

    def _build_quick_lookups(self):
        """Build dictionary lookups for instant access"""

        # Layer 1: condition_name → condition_data
        self.condition_map = {cond['condition']: cond for cond in self.layer1}

        # Layer 2: benefit_name → benefit_data
        self.benefit_map = {
            benefit['benefit_name']: benefit
            for benefit in self.layer2
        }

        # Layer 3: benefit_name → list of conditions
        self.benefit_conditions_map = defaultdict(list)
        for condition in self.layer3:
            benefit_name = condition['benefit_name']
            self.benefit_conditions_map[benefit_name].append(condition)

        # Pre-compute product statistics
        self.product_stats = self._compute_product_stats()

    def _compute_product_stats(self) -> Dict[str, Dict[str, int]]:
        """Pre-compute statistics for each product"""
        stats = {
            product: {
                'total_general_conditions': 0,
                'eligibility_conditions': 0,
                'exclusion_conditions': 0,
                'total_benefits': 0,
                'total_benefit_conditions': 0
            }
            for product in self.products
        }

        # Count Layer 1 conditions
        for condition in self.layer1:
            cond_type = condition['condition_type']
            for product in self.products:
                if condition['products'].get(product,
                                             {}).get('condition_exist', False):
                    stats[product]['total_general_conditions'] += 1
                    if cond_type == 'eligibility':
                        stats[product]['eligibility_conditions'] += 1
                    elif cond_type == 'exclusion':
                        stats[product]['exclusion_conditions'] += 1

        # Count Layer 2 benefits
        for benefit in self.layer2:
            for product in self.products:
                if benefit['products'].get(product,
                                           {}).get('condition_exist', False):
                    stats[product]['total_benefits'] += 1

        # Count Layer 3 conditions
        for condition in self.layer3:
            for product in self.products:
                if condition['products'].get(product,
                                             {}).get('condition_exist', False):
                    stats[product]['total_benefit_conditions'] += 1

        return stats

    # ==================== LAYER 1: GENERAL CONDITIONS QUERIES ====================

    def get_condition(self,
                      condition_name: str,
                      product_name: Optional[str] = None) -> QueryResult:
        """
        Get a specific general condition, optionally filtered by product

        Examples:
            get_condition("trip_start_singapore")
            get_condition("age_eligibility", "Scootsurance")
        """
        if condition_name not in self.condition_map:
            return QueryResult(
                success=False,
                data=None,
                message=f"Condition '{condition_name}' not found")

        condition_data = self.condition_map[condition_name]

        if product_name:
            if product_name not in condition_data['products']:
                return QueryResult(
                    success=False,
                    data=None,
                    message=f"Product '{product_name}' not found in condition")

            return QueryResult(success=True,
                               data={
                                   'condition':
                                   condition_name,
                                   'condition_type':
                                   condition_data['condition_type'],
                                   'product':
                                   product_name,
                                   **condition_data['products'][product_name]
                               })

        return QueryResult(success=True, data=condition_data)

    def check_eligibility(self, product_name: str,
                          user_profile: Dict[str, Any]) -> QueryResult:
        """
        Check if a user meets eligibility requirements for a product

        user_profile: {
            'age': 35,
            'departure_location': 'Singapore',
            'has_pre_existing': False
        }
        """
        eligible = True
        failed_conditions = []
        passed_conditions = []

        for condition in self.layer1:
            if condition['condition_type'] != 'eligibility':
                continue

            product_cond = condition['products'].get(product_name, {})
            if not product_cond.get('condition_exist', False):
                continue

            params = product_cond.get('parameters', {})
            cond_name = condition['condition']

            # Check age eligibility
            if cond_name == 'age_eligibility' and 'age' in user_profile:
                user_age = user_profile['age']
                min_age = params.get('minimum_age', 0)
                max_age = params.get('maximum_age', 999)

                if not (min_age <= user_age <= max_age):
                    eligible = False
                    failed_conditions.append({
                        'condition':
                        cond_name,
                        'reason':
                        f"Age {user_age} outside range {min_age}-{max_age}",
                        'requirement':
                        f"{min_age}-{max_age} years"
                    })
                else:
                    passed_conditions.append(cond_name)

            # Check trip start location
            elif cond_name == 'trip_start_singapore' and 'departure_location' in user_profile:
                required = params.get('departure_location', 'Singapore')
                actual = user_profile['departure_location']

                if actual.lower() != required.lower():
                    eligible = False
                    failed_conditions.append({
                        'condition': cond_name,
                        'reason': f"Trip must start from {required}",
                        'requirement': required
                    })
                else:
                    passed_conditions.append(cond_name)

            else:
                passed_conditions.append(cond_name)

        return QueryResult(success=eligible,
                           data={
                               'product': product_name,
                               'eligible': eligible,
                               'passed_conditions': passed_conditions,
                               'failed_conditions': failed_conditions
                           },
                           message="Eligible" if eligible else "Not eligible")

    def get_all_exclusions(self, product_name: str) -> QueryResult:
        """Get all exclusion conditions for a product"""
        exclusions = []

        for condition in self.layer1:
            if condition['condition_type'] != 'exclusion':
                continue

            product_cond = condition['products'].get(product_name, {})
            if product_cond.get('condition_exist', False):
                exclusions.append({
                    'condition':
                    condition['condition'],
                    'text':
                    product_cond.get('original_text', ''),
                    'parameters':
                    product_cond.get('parameters', {})
                })

        return QueryResult(success=True,
                           data={
                               'product': product_name,
                               'total_exclusions': len(exclusions),
                               'exclusions': exclusions
                           })

    # ==================== LAYER 2: BENEFITS QUERIES ====================

    def get_benefit(self,
                    benefit_name: str,
                    product_name: Optional[str] = None) -> QueryResult:
        """
        Get benefit information, optionally filtered by product

        Examples:
            get_benefit("overseas_medical_expenses")
            get_benefit("accidental_death_permanent_disablement", "Scootsurance")
        """
        if benefit_name not in self.benefit_map:
            return QueryResult(success=False,
                               data=None,
                               message=f"Benefit '{benefit_name}' not found")

        benefit_data = self.benefit_map[benefit_name]

        if product_name:
            if product_name not in benefit_data['products']:
                return QueryResult(
                    success=False,
                    data=None,
                    message=
                    f"Product '{product_name}' does not offer '{benefit_name}'"
                )

            product_benefit = benefit_data['products'][product_name]
            if not product_benefit.get('condition_exist', False):
                return QueryResult(
                    success=False,
                    data=None,
                    message=
                    f"Product '{product_name}' does not offer '{benefit_name}'"
                )

            return QueryResult(success=True,
                               data={
                                   'benefit': benefit_name,
                                   'product': product_name,
                                   **product_benefit
                               })

        return QueryResult(success=True, data=benefit_data)

    def get_all_benefits(self, product_name: str) -> QueryResult:
        """Get all benefits offered by a product"""
        benefits = []

        for benefit in self.layer2:
            product_benefit = benefit['products'].get(product_name, {})
            if product_benefit.get('condition_exist', False):
                benefits.append({
                    'benefit_name':
                    benefit['benefit_name'],
                    'parameters':
                    product_benefit.get('parameters', {})
                })

        return QueryResult(success=True,
                           data={
                               'product': product_name,
                               'total_benefits': len(benefits),
                               'benefits': benefits
                           })

    def compare_benefit_coverage(
            self,
            benefit_name: str,
            products: Optional[List[str]] = None) -> QueryResult:
        """
        Compare how different products cover a specific benefit

        Example:
            compare_benefit_coverage("accidental_death_permanent_disablement")
        """
        if benefit_name not in self.benefit_map:
            return QueryResult(success=False,
                               data=None,
                               message=f"Benefit '{benefit_name}' not found")

        benefit_data = self.benefit_map[benefit_name]
        products_to_compare = products or self.products

        comparison = {'benefit': benefit_name, 'products': {}}

        for product in products_to_compare:
            product_benefit = benefit_data['products'].get(product, {})

            if product_benefit.get('condition_exist', False):
                comparison['products'][product] = {
                    'offered': True,
                    'parameters': product_benefit.get('parameters', {})
                }
            else:
                comparison['products'][product] = {'offered': False}

        return QueryResult(success=True, data=comparison)

    def find_products_with_benefit(self, benefit_name: str) -> QueryResult:
        """Find all products that offer a specific benefit"""
        if benefit_name not in self.benefit_map:
            return QueryResult(success=False,
                               data=None,
                               message=f"Benefit '{benefit_name}' not found")

        benefit_data = self.benefit_map[benefit_name]
        products_with_benefit = []

        for product in self.products:
            product_benefit = benefit_data['products'].get(product, {})
            if product_benefit.get('condition_exist', False):
                products_with_benefit.append({
                    'product':
                    product,
                    'parameters':
                    product_benefit.get('parameters', {})
                })

        return QueryResult(success=True,
                           data={
                               'benefit': benefit_name,
                               'total_products': len(products_with_benefit),
                               'products': products_with_benefit
                           })

    # ==================== LAYER 3: BENEFIT-SPECIFIC CONDITIONS ====================

    def get_benefit_conditions(
            self,
            benefit_name: str,
            product_name: Optional[str] = None) -> QueryResult:
        """
        Get all conditions for a specific benefit

        Example:
            get_benefit_conditions("accidental_death_permanent_disablement", "Scootsurance")
        """
        if benefit_name not in self.benefit_conditions_map:
            return QueryResult(
                success=False,
                data=None,
                message=f"No conditions found for benefit '{benefit_name}'")

        conditions = self.benefit_conditions_map[benefit_name]

        if product_name:
            product_conditions = []
            for condition in conditions:
                product_cond = condition['products'].get(product_name, {})
                if product_cond.get('condition_exist', False):
                    product_conditions.append({
                        'condition':
                        condition['condition'],
                        'condition_type':
                        condition['condition_type'],
                        'original_text':
                        product_cond.get('original_text', ''),
                        'parameters':
                        product_cond.get('parameters', {})
                    })

            return QueryResult(success=True,
                               data={
                                   'benefit': benefit_name,
                                   'product': product_name,
                                   'total_conditions': len(product_conditions),
                                   'conditions': product_conditions
                               })

        return QueryResult(success=True,
                           data={
                               'benefit': benefit_name,
                               'conditions': conditions
                           })

    def check_benefit_eligibility(self, benefit_name: str, product_name: str,
                                  scenario: Dict[str, Any]) -> QueryResult:
        """
        Check if a scenario qualifies for a benefit

        scenario: {
            'days_since_accident': 45,
            'injury_type': 'permanent_disablement'
        }
        """
        if benefit_name not in self.benefit_conditions_map:
            return QueryResult(success=False,
                               data=None,
                               message=f"Benefit '{benefit_name}' not found")

        conditions = self.benefit_conditions_map[benefit_name]
        eligible = True
        checks = []

        for condition in conditions:
            product_cond = condition['products'].get(product_name, {})
            if not product_cond.get('condition_exist', False):
                continue

            cond_name = condition['condition']
            cond_type = condition['condition_type']
            params = product_cond.get('parameters', {})

            # Example: Check time limits
            if 'time_limit' in cond_name and 'days_since_accident' in scenario:
                if 'death_time_limit' in params and scenario.get(
                        'injury_type') == 'death':
                    limit = params['death_time_limit']
                    actual = scenario['days_since_accident']

                    if actual > limit:
                        eligible = False
                        checks.append({
                            'condition':
                            cond_name,
                            'passed':
                            False,
                            'reason':
                            f"Claim filed {actual} days after accident, limit is {limit} days"
                        })
                    else:
                        checks.append({'condition': cond_name, 'passed': True})

                elif 'permanent_disablement_time_limit' in params and scenario.get(
                        'injury_type') == 'permanent_disablement':
                    limit = params['permanent_disablement_time_limit']
                    actual = scenario['days_since_accident']

                    if actual > limit:
                        eligible = False
                        checks.append({
                            'condition':
                            cond_name,
                            'passed':
                            False,
                            'reason':
                            f"Claim filed {actual} days after accident, limit is {limit} days"
                        })
                    else:
                        checks.append({'condition': cond_name, 'passed': True})

        return QueryResult(success=eligible,
                           data={
                               'benefit': benefit_name,
                               'product': product_name,
                               'eligible': eligible,
                               'checks': checks
                           })

    # ==================== PRODUCT-LEVEL QUERIES ====================

    def get_product_summary(self, product_name: str) -> QueryResult:
        """Get comprehensive summary of a product"""
        if product_name not in self.products:
            return QueryResult(success=False,
                               data=None,
                               message=f"Product '{product_name}' not found")

        stats = self.product_stats[product_name]

        # Get key conditions
        eligibility_conditions = []
        for condition in self.layer1:
            if condition['condition_type'] == 'eligibility':
                product_cond = condition['products'].get(product_name, {})
                if product_cond.get('condition_exist', False):
                    eligibility_conditions.append({
                        'condition':
                        condition['condition'],
                        'text':
                        product_cond.get('original_text', ''),
                        'parameters':
                        product_cond.get('parameters', {})
                    })

        # Get all benefits
        benefits_result = self.get_all_benefits(product_name)

        return QueryResult(success=True,
                           data={
                               'product': product_name,
                               'statistics': stats,
                               'eligibility_conditions':
                               eligibility_conditions,
                               'benefits': benefits_result.data['benefits']
                           })

    def compare_products(self,
                         products: Optional[List[str]] = None) -> QueryResult:
        """High-level comparison of products"""
        products_to_compare = products or self.products

        comparison = {'products': {}, 'best_in_category': {}}

        for product in products_to_compare:
            comparison['products'][product] = self.product_stats[product]

        # Find best in categories
        comparison['best_in_category'] = {
            'most_benefits':
            max(products_to_compare,
                key=lambda p: self.product_stats[p]['total_benefits']),
            'least_exclusions':
            min(products_to_compare,
                key=lambda p: self.product_stats[p]['exclusion_conditions']),
            'simplest_eligibility':
            min(products_to_compare,
                key=lambda p: self.product_stats[p]['eligibility_conditions'])
        }

        return QueryResult(success=True, data=comparison)

    # ==================== SMART RECOMMENDATION ====================

    def recommend_product(self, user_profile: Dict[str, Any],
                          priority_benefits: List[str]) -> QueryResult:
        """
        Recommend best product based on user profile and priorities

        user_profile: {'age': 35, 'departure_location': 'Singapore'}
        priority_benefits: ['overseas_medical_expenses', 'trip_cancellation']
        """
        rankings = []

        for product in self.products:
            score = 0
            reasons = []

            # Check eligibility
            eligibility = self.check_eligibility(product, user_profile)
            if not eligibility.success:
                continue  # Skip ineligible products

            # Score based on priority benefits
            covered_benefits = []
            for benefit in priority_benefits:
                benefit_result = self.get_benefit(benefit, product)
                if benefit_result.success:
                    score += 10
                    covered_benefits.append(benefit)

            # Bonus for total benefits offered
            all_benefits = self.get_all_benefits(product)
            score += all_benefits.data['total_benefits'] * 0.5

            # Penalty for exclusions
            exclusions = self.get_all_exclusions(product)
            score -= exclusions.data['total_exclusions'] * 0.3

            rankings.append({
                'product':
                product,
                'score':
                round(score, 2),
                'covered_priority_benefits':
                covered_benefits,
                'missing_priority_benefits':
                [b for b in priority_benefits if b not in covered_benefits],
                'total_benefits':
                all_benefits.data['total_benefits'],
                'total_exclusions':
                exclusions.data['total_exclusions']
            })

        rankings.sort(key=lambda x: x['score'], reverse=True)

        if not rankings:
            return QueryResult(
                success=False,
                data=None,
                message="No products meet eligibility requirements")

        return QueryResult(success=True,
                           data={
                               'recommended_product':
                               rankings[0]['product'],
                               'score':
                               rankings[0]['score'],
                               'reasoning':
                               rankings[0],
                               'alternatives':
                               rankings[1:3] if len(rankings) > 1 else [],
                               'all_rankings':
                               rankings
                           })


# ==================== USAGE EXAMPLES ====================


def example_get_condition(query_engine, condition_name, product_name=None):
    """Example: Get a specific condition"""
    print(f"\n{'='*70}")
    print(f"Example: Get condition '{condition_name}'" +
          (f" for '{product_name}'" if product_name else ""))
    print('=' * 70)

    result = query_engine.get_condition(condition_name, product_name)
    if result.success:
        print("✓ Success!")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"✗ Failed: {result.message}")
    return result


def example_check_eligibility(query_engine, product_name, user_profile):
    """Example: Check if user is eligible for a product"""
    print(f"\n{'='*70}")
    print(f"Example: Check eligibility for '{product_name}'")
    print(f"User profile: {user_profile}")
    print('=' * 70)

    result = query_engine.check_eligibility(product_name, user_profile)
    print(f"Eligible: {result.success}")
    print(json.dumps(result.data, indent=2))
    return result


def example_get_all_exclusions(query_engine, product_name):
    """Example: Get all exclusions for a product"""
    print(f"\n{'='*70}")
    print(f"Example: Get all exclusions for '{product_name}'")
    print('=' * 70)

    result = query_engine.get_all_exclusions(product_name)
    if result.success:
        print(f"✓ Found {result.data['total_exclusions']} exclusions")
        for exclusion in result.data['exclusions']:
            print(f"\n  • {exclusion['condition']}")
            print(f"    {exclusion['text'][:100]}...")
    return result


def example_get_benefit(query_engine, benefit_name, product_name=None):
    """Example: Get benefit information"""
    print(f"\n{'='*70}")
    print(f"Example: Get benefit '{benefit_name}'" +
          (f" for '{product_name}'" if product_name else ""))
    print('=' * 70)

    result = query_engine.get_benefit(benefit_name, product_name)
    if result.success:
        print("✓ Success!")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"✗ Failed: {result.message}")
    return result


def example_get_all_benefits(query_engine, product_name):
    """Example: Get all benefits for a product"""
    print(f"\n{'='*70}")
    print(f"Example: Get all benefits for '{product_name}'")
    print('=' * 70)

    result = query_engine.get_all_benefits(product_name)
    if result.success:
        print(f"✓ Found {result.data['total_benefits']} benefits:")
        for benefit in result.data['benefits']:
            print(f"\n  • {benefit['benefit_name']}")
            if benefit['parameters']:
                print(
                    f"    Parameters: {json.dumps(benefit['parameters'], indent=6)}"
                )
    return result


def example_compare_benefit_coverage(query_engine,
                                     benefit_name,
                                     products=None):
    """Example: Compare how products cover a benefit"""
    print(f"\n{'='*70}")
    print(f"Example: Compare '{benefit_name}' across products")
    print('=' * 70)

    result = query_engine.compare_benefit_coverage(benefit_name, products)
    if result.success:
        print("✓ Comparison:")
        for product, details in result.data['products'].items():
            print(f"\n  {product}:")
            if details['offered']:
                print(f"    ✓ Offered")
                if details.get('parameters'):
                    print(
                        f"    Coverage: {json.dumps(details['parameters'], indent=6)}"
                    )
            else:
                print(f"    ✗ Not offered")
    return result


def example_find_products_with_benefit(query_engine, benefit_name):
    """Example: Find which products offer a benefit"""
    print(f"\n{'='*70}")
    print(f"Example: Find products offering '{benefit_name}'")
    print('=' * 70)

    result = query_engine.find_products_with_benefit(benefit_name)
    if result.success:
        print(
            f"✓ {result.data['total_products']} products offer this benefit:")
        for product_info in result.data['products']:
            print(f"\n  • {product_info['product']}")
            if product_info['parameters']:
                print(
                    f"    {json.dumps(product_info['parameters'], indent=6)}")
    return result


def example_get_benefit_conditions(query_engine,
                                   benefit_name,
                                   product_name=None):
    """Example: Get conditions for a benefit"""
    print(f"\n{'='*70}")
    print(f"Example: Get conditions for benefit '{benefit_name}'" +
          (f" in '{product_name}'" if product_name else ""))
    print('=' * 70)

    result = query_engine.get_benefit_conditions(benefit_name, product_name)
    if result.success:
        if product_name:
            print(f"✓ Found {result.data['total_conditions']} conditions:")
            for condition in result.data['conditions']:
                print(
                    f"\n  • {condition['condition']} ({condition['condition_type']})"
                )
                print(f"    {condition['original_text'][:100]}...")
        else:
            print(f"✓ Found {len(result.data['conditions'])} conditions")
    return result


def example_get_product_summary(query_engine, product_name):
    """Example: Get comprehensive product summary"""
    print(f"\n{'='*70}")
    print(f"Example: Get summary for '{product_name}'")
    print('=' * 70)

    result = query_engine.get_product_summary(product_name)
    if result.success:
        print("✓ Product Summary:")
        print(f"\n  Statistics:")
        for key, value in result.data['statistics'].items():
            print(f"    {key}: {value}")

        print(
            f"\n  Eligibility Conditions: {len(result.data['eligibility_conditions'])}"
        )
        print(f"  Total Benefits: {len(result.data['benefits'])}")
    return result


def example_compare_products(query_engine, products=None):
    """Example: Compare all products"""
    print(f"\n{'='*70}")
    print(f"Example: Compare products" +
          (f": {products}" if products else " (all)"))
    print('=' * 70)

    result = query_engine.compare_products(products)
    if result.success:
        print("✓ Product Comparison:")

        print("\n  Statistics by Product:")
        for product, stats in result.data['products'].items():
            print(f"\n  {product}:")
            for key, value in stats.items():
                print(f"    {key}: {value}")

        print("\n  Best in Category:")
        for category, product in result.data['best_in_category'].items():
            print(f"    {category}: {product}")
    return result


def example_recommend_product(query_engine, user_profile, priority_benefits):
    """Example: Get product recommendation"""
    print(f"\n{'='*70}")
    print(f"Example: Recommend product")
    print(f"User profile: {user_profile}")
    print(f"Priority benefits: {priority_benefits}")
    print('=' * 70)

    result = query_engine.recommend_product(user_profile, priority_benefits)
    if result.success:
        print(f"\n✓ Recommended Product: {result.data['recommended_product']}")
        print(f"  Score: {result.data['score']}")
        print(
            f"  Covered benefits: {result.data['reasoning']['covered_priority_benefits']}"
        )
        print(
            f"  Missing benefits: {result.data['reasoning']['missing_priority_benefits']}"
        )

        if result.data['alternatives']:
            print("Alternatives:")
            for alt in result.data['alternatives']:
                print(f"    • {alt['product']} (Score: {alt['score']})")
    else:
        print(f"✗ Failed: {result.message}")
    return result


if __name__ == "__main__":
    # Initialize query engine with your file
    FILE_PATH = './Server/Taxonomy_Hackathon.json'

    print("=" * 70)
    print("LOADING TRAVEL INSURANCE DATA")
    print("=" * 70)

    query = TravelInsuranceQuery(FILE_PATH)

    print(f"\nAvailable products: {query.products}")

    # Run example queries - modify these as needed!

    # Example 1: Get specific condition
    example_get_condition(query, "trip_start_singapore", query.products[0])

    # Example 2: Check eligibility
    user_profile = {'age': 35, 'departure_location': 'Singapore'}
    example_check_eligibility(query, query.products[0], user_profile)

    # Example 3: Get all exclusions
    example_get_all_exclusions(query, query.products[0])

    # Example 4: Get specific benefit
    example_get_benefit(query, "accidental_death_permanent_disablement",
                        query.products[0])

    # Example 5: Get all benefits
    example_get_all_benefits(query, query.products[0])

    # Example 6: Compare benefit coverage
    example_compare_benefit_coverage(query,
                                     "accidental_death_permanent_disablement")

    # Example 7: Find products with benefit
    example_find_products_with_benefit(
        query, "accidental_death_permanent_disablement")

    # Example 8: Get benefit conditions
    example_get_benefit_conditions(query,
                                   "accidental_death_permanent_disablement",
                                   query.products[0])

    # Example 9: Get product summary
    example_get_product_summary(query, query.products[0])

    # Example 10: Compare all products
    example_compare_products(query)

    # Example 11: Get recommendation
    priority_benefits = [
        'accidental_death_permanent_disablement', 'overseas_medical_expenses'
    ]
    example_recommend_product(query, user_profile, priority_benefits)
