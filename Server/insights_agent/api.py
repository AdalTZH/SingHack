"""
API interface for the Insights Agent
Provides a clean interface for integrating with the insights agent
"""
from .insights_agent import InsightsAgent
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightsAgentAPI:
    """API wrapper for Insights Agent"""
    
    def __init__(self, model_name: Optional[str] = None, temperature: Optional[float] = None):
        """
        Initialize the Insights Agent API
        
        Args:
            model_name: OpenAI model name (optional)
            temperature: Temperature for LLM (optional)
        """
        self.agent = InsightsAgent(model_name=model_name, temperature=temperature)
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main API method for processing queries and determining if analytics should be performed
        
        Args:
            user_query: User's query/question
            
        Returns:
            Dictionary with insights and metadata
        """
        try:
            result = self.agent.process_query(user_query)
            return result
        
        except Exception as e:
            logger.error(f"Error in Insights Agent API: {e}")
            return {
                'should_analyze': False,
                'performed_analytics': False,
                'insights': None,
                'reasoning': f'Error: {str(e)}',
                'confidence': 0.0,
                'error': str(e)
            }

