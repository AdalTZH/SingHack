"""
Predict Agent Package
Provides insurance plan recommendations based on historical claims data
"""

from .api import PredictAgentAPI, get_insurance_recommendations
from .predict_agent import PredictAgent
from .user_data_model import UserData

try:
    from .mcp_server import mcp_server
    __all__ = [
        'PredictAgentAPI',
        'get_insurance_recommendations',
        'PredictAgent',
        'UserData',
        'mcp_server'
    ]
except ImportError:
    __all__ = [
        'PredictAgentAPI',
        'get_insurance_recommendations',
        'PredictAgent',
        'UserData'
    ]

