"""
API interface for the Predict Agent
Provides a clean interface for teammates to integrate with
"""
from .predict_agent import PredictAgent
from .user_data_model import UserData
from typing import Dict, Any, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictAgentAPI:
    """API wrapper for Predict Agent"""
    
    def __init__(self):
        self.agent = PredictAgent()
    
    def predict(self, user_data_dict: Dict[str, Any], top_n: int = 3) -> Dict[str, Any]:
        """
        Main API method for getting insurance plan predictions
        
        Args:
            user_data_dict: Dictionary containing user data (as collected by teammates)
            top_n: Number of top recommendations to return (default: 3)
            
        Returns:
            Dictionary with recommendations and metadata
        """
        try:
            # Convert dict to UserData object
            user_data = self._dict_to_user_data(user_data_dict)
            
            # Get predictions
            recommendations = self.agent.predict_best_plan(user_data, top_n)
            
            return {
                'success': True,
                'user_profile': {
                    'age': user_data.age,
                    'destination': user_data.travel_destination,
                    'trip_duration': user_data.trip_duration_days
                },
                'recommendations': recommendations,
                'total_recommendations': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in predict API: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def _dict_to_user_data(self, data_dict: Dict[str, Any]) -> UserData:
        """Convert dictionary to UserData object"""
        return UserData(
            age=data_dict.get('age'),
            travel_destination=data_dict.get('travel_destination', ''),
            trip_duration_days=data_dict.get('trip_duration_days', 7),
            trip_type=data_dict.get('trip_type'),
            travel_style=data_dict.get('travel_style'),
            has_pre_existing_conditions=data_dict.get('has_pre_existing_conditions', False),
            plans_adventure_activities=data_dict.get('plans_adventure_activities', False),
            traveling_with_children=data_dict.get('traveling_with_children', False),
            traveling_with_valuables=data_dict.get('traveling_with_valuables', False),
            priority_medical_coverage=data_dict.get('priority_medical_coverage', True),
            priority_trip_cancellation=data_dict.get('priority_trip_cancellation', False),
            priority_baggage_coverage=data_dict.get('priority_baggage_coverage', False),
            priority_liability_coverage=data_dict.get('priority_liability_coverage', False),
            budget_range=data_dict.get('budget_range'),
            frequent_traveler=data_dict.get('frequent_traveler', False),
            previous_claims=data_dict.get('previous_claims', 0)
        )
    
    def get_recommendations_json(self, user_data_dict: Dict[str, Any], top_n: int = 3) -> str:
        """Get predictions as JSON string"""
        result = self.predict(user_data_dict, top_n)
        return json.dumps(result, indent=2)


# Convenience function for easy integration
def get_insurance_recommendations(user_data: Dict[str, Any], top_n: int = 3) -> Dict[str, Any]:
    """
    Convenience function for getting insurance recommendations
    
    Usage:
        result = get_insurance_recommendations({
            'age': 35,
            'travel_destination': 'Japan',
            'trip_duration_days': 10,
            'priority_medical_coverage': True
        })
    """
    api = PredictAgentAPI()
    return api.predict(user_data, top_n)

