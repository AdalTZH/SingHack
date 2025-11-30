"""
Layer 1 Exclusions Query Script
Focused script for querying exclusion conditions from travel insurance policies
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ExclusionResult:
    """Structure for exclusion query results"""
    product: str
    total_exclusions: int
    exclusions: List[Dict[str, Any]]
    success: bool = True
    message: str = ""


class Layer1ExclusionsQuery:
    """
    Specialized query engine for Layer 1 exclusion conditions
    """

    def __init__(self, json_file_path: str):
        """Load the JSON file and extract Layer 1 data"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.products = self.data.get('products', [])
        self.layer1 = self.data['layers']['layer_1_general_conditions']

        # Filter only exclusion conditions
        self.exclusion_conditions = [
            cond for cond in self.layer1
            if cond['condition_type'] == 'exclusion'
        ]

        print(f"✓ Loaded {len(self.products)} products")
        print(f"✓ Found {len(self.exclusion_conditions)} exclusion conditions in Layer 1")

    def get_exclusions_for_product(self, product_name: str) -> ExclusionResult:
        """
        Get all exclusion conditions for a specific product
        
        Args:
            product_name: Name of the insurance product
            
        Returns:
            ExclusionResult object containing all exclusions
        """
        if product_name not in self.products:
            return ExclusionResult(
                product=product_name,
                total_exclusions=0,
                exclusions=[],
                success=False,
                message=f"Product '{product_name}' not found. Available products: {', '.join(self.products)}"
            )

        exclusions = []

        for condition in self.exclusion_conditions:
            product_cond = condition['products'].get(product_name, {})
            
            if product_cond.get('condition_exist', False):
                exclusion_entry = {
                    'condition_name': condition['condition'],
                    'original_text': product_cond.get('original_text', ''),
                    'parameters': product_cond.get('parameters', {}),
                    'condition_type': condition['condition_type']
                }
                exclusions.append(exclusion_entry)

        return ExclusionResult(
            product=product_name,
            total_exclusions=len(exclusions),
            exclusions=exclusions,
            success=True,
            message=f"Found {len(exclusions)} exclusions for {product_name}"
        )

    def display_exclusions(self, product_name: str, detailed: bool = True) -> None:
        """
        Display exclusions for a product in a formatted way
        
        Args:
            product_name: Name of the insurance product
            detailed: If True, shows full text and parameters. If False, shows summary only
        """
        result = self.get_exclusions_for_product(product_name)

        print("\n" + "=" * 80)
        print(f"EXCLUSIONS FOR: {product_name}")
        print("=" * 80)

        if not result.success:
            print(f"✗ Error: {result.message}")
            return

        print(f"Total Exclusions: {result.total_exclusions}\n")

        if result.total_exclusions == 0:
            print("No exclusions found for this product.")
            return

        for idx, exclusion in enumerate(result.exclusions, 1):
            print(f"{idx}. {exclusion['condition_name']}")
            print("-" * 80)

            if detailed:
                # Show original text
                text = exclusion['original_text']
                if text:
                    print(f"Description:")
                    print(f"  {text}\n")
                
                # Show parameters if any
                if exclusion['parameters']:
                    print(f"Parameters:")
                    for key, value in exclusion['parameters'].items():
                        print(f"  • {key}: {value}")
                    print()
            else:
                # Just show a preview of the text
                text = exclusion['original_text']
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"  {preview}\n")

    def compare_exclusions_across_products(
        self, 
        products: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare exclusions across multiple products
        
        Args:
            products: List of product names to compare. If None, compares all products.
            
        Returns:
            Dictionary with comparison data
        """
        products_to_compare = products or self.products
        comparison = {
            'products': {},
            'summary': {
                'most_restrictive': None,
                'least_restrictive': None,
                'common_exclusions': []
            }
        }

        # Get exclusions for each product
        for product in products_to_compare:
            result = self.get_exclusions_for_product(product)
            if result.success:
                comparison['products'][product] = {
                    'total_exclusions': result.total_exclusions,
                    'exclusion_names': [e['condition_name'] for e in result.exclusions]
                }

        # Find most and least restrictive
        if comparison['products']:
            sorted_by_count = sorted(
                comparison['products'].items(),
                key=lambda x: x[1]['total_exclusions'],
                reverse=True
            )
            comparison['summary']['most_restrictive'] = sorted_by_count[0][0]
            comparison['summary']['least_restrictive'] = sorted_by_count[-1][0]

            # Find common exclusions (present in all products)
            all_exclusions = [
                set(data['exclusion_names']) 
                for data in comparison['products'].values()
            ]
            if all_exclusions:
                common = set.intersection(*all_exclusions)
                comparison['summary']['common_exclusions'] = list(common)

        return comparison

    def display_comparison(self, products: Optional[List[str]] = None) -> None:
        """
        Display a formatted comparison of exclusions across products
        
        Args:
            products: List of product names to compare. If None, compares all products.
        """
        comparison = self.compare_exclusions_across_products(products)

        print("\n" + "=" * 80)
        print("EXCLUSIONS COMPARISON ACROSS PRODUCTS")
        print("=" * 80)

        print("\nExclusions Count by Product:")
        print("-" * 80)
        for product, data in comparison['products'].items():
            print(f"{product:40} {data['total_exclusions']} exclusions")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        summary = comparison['summary']
        print(f"Most Restrictive Product:  {summary['most_restrictive']}")
        print(f"Least Restrictive Product: {summary['least_restrictive']}")
        
        print(f"\nCommon Exclusions (in all products): {len(summary['common_exclusions'])}")
        for exclusion in summary['common_exclusions']:
            print(f"  • {exclusion}")

    def search_exclusion_by_keyword(
        self, 
        keyword: str, 
        product_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for exclusions containing a specific keyword
        
        Args:
            keyword: Keyword to search for in exclusion names or text
            product_name: If specified, searches only in that product
            
        Returns:
            List of matching exclusions
        """
        keyword_lower = keyword.lower()
        matches = []

        products_to_search = [product_name] if product_name else self.products

        for product in products_to_search:
            result = self.get_exclusions_for_product(product)
            
            if result.success:
                for exclusion in result.exclusions:
                    # Search in condition name and original text
                    if (keyword_lower in exclusion['condition_name'].lower() or
                        keyword_lower in exclusion['original_text'].lower()):
                        
                        matches.append({
                            'product': product,
                            'condition_name': exclusion['condition_name'],
                            'original_text': exclusion['original_text'],
                            'parameters': exclusion['parameters']
                        })

        return matches


# ==================== EXAMPLE USAGE ====================

def main():
    """Example usage of the Layer 1 Exclusions Query script"""
    
    # Initialize the query engine
    FILE_PATH = './Server/Taxonomy_Hackathon.json'
    
    print("=" * 80)
    print("LAYER 1 EXCLUSIONS QUERY TOOL")
    print("=" * 80)
    
    query = Layer1ExclusionsQuery(FILE_PATH)
    
    print(f"\nAvailable products: {', '.join(query.products)}")
    
    # Example 1: Display exclusions for first product (detailed view)
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Detailed Exclusions List")
    print("=" * 80)
    query.display_exclusions(query.products[0], detailed=True)
    
    # Example 2: Display exclusions for first product (summary view)
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Summary Exclusions List")
    print("=" * 80)
    query.display_exclusions(query.products[0], detailed=False)
    
    # Example 3: Compare exclusions across all products
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Compare All Products")
    print("=" * 80)
    query.display_comparison()
    
    # Example 4: Search for specific exclusion keyword
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Search for 'war' in exclusions")
    print("=" * 80)
    matches = query.search_exclusion_by_keyword('war')
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(f"\n  Product: {match['product']}")
        print(f"  Condition: {match['condition_name']}")
        print(f"  Text: {match['original_text'][:100]}...")
    
    # Example 5: Get exclusions programmatically
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Programmatic Access")
    print("=" * 80)
    result = query.get_exclusions_for_product(query.products[0])
    print(f"Product: {result.product}")
    print(f"Success: {result.success}")
    print(f"Total Exclusions: {result.total_exclusions}")
    print(f"Message: {result.message}")


if __name__ == "__main__":
    main()