"""
Example usage of the Predict Agent
Demonstrates how teammates can integrate the predict agent
"""
from .api import get_insurance_recommendations
from .predict_agent import PredictAgent
from .user_data_model import UserData
import json

def example_1_simple_usage():
    """Simple API usage example"""
    print("=" * 60)
    print("Example 1: Simple API Usage")
    print("=" * 60)
    
    # User data as dictionary (as collected by teammates)
    user_data = {
        'age': 35,
        'travel_destination': 'Japan',
        'trip_duration_days': 10,
        'priority_medical_coverage': True,
        'trip_type': 'leisure'
    }
    
    # Get recommendations
    result = get_insurance_recommendations(user_data, top_n=3)
    
    # Print results
    print(json.dumps(result, indent=2))
    print("\n")


def example_2_comprehensive_user_profile():
    """Comprehensive user profile example"""
    print("=" * 60)
    print("Example 2: Comprehensive User Profile")
    print("=" * 60)
    
    user_data = {
        'age': 28,
        'travel_destination': 'Thailand',
        'trip_duration_days': 14,
        'trip_type': 'adventure',
        'travel_style': 'backpacking',
        'has_pre_existing_conditions': False,
        'plans_adventure_activities': True,
        'traveling_with_children': False,
        'traveling_with_valuables': True,
        'priority_medical_coverage': True,
        'priority_trip_cancellation': False,
        'priority_baggage_coverage': True,
        'priority_liability_coverage': False,
        'budget_range': 'medium',
        'frequent_traveler': True,
        'previous_claims': 0
    }
    
    result = get_insurance_recommendations(user_data, top_n=5)
    
    print(f"Success: {result['success']}")
    print(f"User: {result['user_profile']}")
    print(f"\nTop {result['total_recommendations']} Recommendations:")
    
    for rec in result['recommendations']:
        print(f"\n{rec['rank']}. {rec['product_name']} ({rec['product_category']})")
        print(f"   Score: {rec['composite_score']}")
        print(f"   Reasoning: {rec['reasoning']}")
        print(f"   Stats: {rec['stats']}")
    print("\n")


def example_3_direct_agent_usage():
    """Direct agent usage (for more control)"""
    print("=" * 60)
    print("Example 3: Direct Agent Usage")
    print("=" * 60)
    
    # Create user data object directly
    user_data = UserData(
        age=45,
        travel_destination='Australia',
        trip_duration_days=21,
        priority_medical_coverage=True,
        priority_trip_cancellation=True,
        plans_adventure_activities=False
    )
    
    # Use agent directly
    agent = PredictAgent()
    recommendations = agent.predict_best_plan(user_data, top_n=3)
    
    print(f"Recommendations for {user_data.travel_destination}:")
    for rec in recommendations:
        print(f"\n{rec['rank']}. {rec['product_name']}")
        print(f"   Composite Score: {rec['composite_score']}")
        print(f"   Reasoning: {rec['reasoning']}")
    print("\n")


# Note: When running as a script from within the package, use:
# python -m predict_agent.example_usage
# Or import and call functions from outside the package

def main():
    print("\n" + "=" * 60)
    print("PREDICT AGENT - EXAMPLE USAGE")
    print("=" * 60 + "\n")
    
    try:
        example_1_simple_usage()
        example_2_comprehensive_user_profile()
        example_3_direct_agent_usage()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

