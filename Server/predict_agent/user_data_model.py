"""
User data model for prediction input
This defines the structure of user data that will be collected by teammates
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import date


@dataclass
class UserData:
    """User data model for insurance prediction"""
    # Basic Information
    age: int
    travel_destination: str
    trip_duration_days: int
    
    # Trip Details
    trip_type: Optional[str] = None  # e.g., "business", "leisure", "adventure"
    travel_style: Optional[str] = None  # e.g., "budget", "luxury", "backpacking"
    
    # Risk Factors
    has_pre_existing_conditions: Optional[bool] = False
    plans_adventure_activities: Optional[bool] = False
    traveling_with_children: Optional[bool] = False
    traveling_with_valuables: Optional[bool] = False
    
    # Coverage Preferences
    priority_medical_coverage: Optional[bool] = True
    priority_trip_cancellation: Optional[bool] = False
    priority_baggage_coverage: Optional[bool] = False
    priority_liability_coverage: Optional[bool] = False
    
    # Budget
    budget_range: Optional[str] = None  # e.g., "low", "medium", "high"
    
    # Additional Risk Indicators
    frequent_traveler: Optional[bool] = False
    previous_claims: Optional[int] = 0
    
    def to_dict(self):
        """Convert to dictionary for easier processing"""
        return {
            'age': self.age,
            'travel_destination': self.travel_destination,
            'trip_duration_days': self.trip_duration_days,
            'trip_type': self.trip_type,
            'travel_style': self.travel_style,
            'has_pre_existing_conditions': self.has_pre_existing_conditions,
            'plans_adventure_activities': self.plans_adventure_activities,
            'traveling_with_children': self.traveling_with_children,
            'traveling_with_valuables': self.traveling_with_valuables,
            'priority_medical_coverage': self.priority_medical_coverage,
            'priority_trip_cancellation': self.priority_trip_cancellation,
            'priority_baggage_coverage': self.priority_baggage_coverage,
            'priority_liability_coverage': self.priority_liability_coverage,
            'budget_range': self.budget_range,
            'frequent_traveler': self.frequent_traveler,
            'previous_claims': self.previous_claims
        }

