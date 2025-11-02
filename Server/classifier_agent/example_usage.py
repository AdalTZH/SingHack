"""
Example usage of the Classifier Agent
Demonstrates how to classify insurance queries
"""

from .api import classify_query, classify_query_detailed, classify_batch
from .classifier_agent import ClassifierAgent
from .taxonomy_loader import get_taxonomy_loader


def example_1_simple_classification():
    """Example 1: Simple classification"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Classification")
    print("="*80)
    
    query = "Which plan has better medical coverage?"
    classification = classify_query(query)
    
    print(f"\nQuery: {query}")
    print(f"Classification: {classification}")
    print(f"\n✓ Query successfully classified as '{classification}'")


def example_2_detailed_classification():
    """Example 2: Detailed classification with reasoning"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Detailed Classification")
    print("="*80)
    
    query = "What is covered under home contents insurance?"
    result = classify_query_detailed(query)
    
    print(f"\nQuery: {query}")
    print(f"\nClassification: {result['classification']}")
    print(f"Type: {result['type_details']['name']}")
    print(f"Description: {result['type_details']['description']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nReasoning: {result['reasoning']}")
    print(f"\nNext Steps: {result['type_details']['next_steps']}")
    print(f"\n✓ Detailed classification retrieved successfully")


def example_3_batch_classification():
    """Example 3: Batch classification"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Classification")
    print("="*80)
    
    queries = [
        "Compare Product A and Product B for baggage coverage",
        "What does medical insurance cover?",
        "Am I covered for skiing injuries?",
        "What happens if I break my leg abroad?"
    ]
    
    print(f"\nClassifying {len(queries)} queries:")
    results = classify_batch(queries)
    
    for i, (query, result) in enumerate(zip(queries, results), 1):
        print(f"\n{i}. Query: {query}")
        print(f"   Classification: {result['classification']}")
        print(f"   Confidence: {result['confidence']:.2f}")
    
    print(f"\n✓ Batch classification completed successfully")


def example_4_classification_types():
    """Example 4: Demonstrate all four classification types"""
    print("\n" + "="*80)
    print("EXAMPLE 4: All Classification Types")
    print("="*80)
    
    examples = {
        'comparison': [
            "Which plan has better medical coverage?",
            "Compare Product A and Product C",
            "What's the difference between travel insurance plans?"
        ],
        'explanation': [
            "What is covered under home contents?",
            "Explain how medical evacuation works",
            "What does trip cancellation mean?"
        ],
        'eligibility': [
            "Am I covered for pre-existing conditions?",
            "Can I claim for skiing injuries?",
            "Am I eligible for dental coverage at age 70?"
        ],
        'scenario_analysis': [
            "What happens if I break my leg skiing in Japan?",
            "What if my flight is delayed for 24 hours?",
            "In case of a natural disaster, am I covered?"
        ]
    }
    
    agent = ClassifierAgent()
    
    for query_type, queries in examples.items():
        print(f"\n{'-'*80}")
        print(f"{query_type.upper()} Examples:")
        print('-'*80)
        
        for query in queries:
            result = agent.classify(query)
            print(f"\nQuery: {query}")
            print(f"Classified as: {result['classification']} "
                  f"(confidence: {result['confidence']:.2f})")
    
    print(f"\n✓ All classification types demonstrated successfully")


def example_5_taxonomy_loader():
    """Example 5: Using the taxonomy loader directly"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Taxonomy Loader")
    print("="*80)
    
    loader = get_taxonomy_loader()
    
    # Get taxonomy structure
    structure = loader.get_taxonomy_structure()
    print(f"\nTaxonomy Name: {structure['name']}")
    print(f"Products: {', '.join(structure['products'])}")
    print(f"Layers: {', '.join(structure['layers'])}")
    
    # Get a benefit
    benefit = loader.get_benefit_by_name('home_contents')
    if benefit:
        print(f"\nBenefit: {benefit['benefit_name']}")
        print(f"Products with this benefit:")
        for product_name, product_data in benefit.get('products', {}).items():
            has_condition = product_data.get('condition_exist', False)
            print(f"  - {product_name}: condition_exist = {has_condition}")
    
    # Get all benefit names
    benefits = loader.get_benefit_names()
    print(f"\nTotal benefits in taxonomy: {len(benefits)}")
    print(f"First 10 benefits: {', '.join(benefits[:10])}")
    
    print(f"\n✓ Taxonomy loader working correctly")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*80)
    print("CLASSIFIER AGENT - EXAMPLE USAGE")
    print("="*80)
    
    try:
        example_1_simple_classification()
        example_2_detailed_classification()
        example_3_batch_classification()
        example_4_classification_types()
        example_5_taxonomy_loader()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()

