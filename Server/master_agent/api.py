"""
API interface for the Master Agent
Provides a clean interface for integrating with the master agent
"""
from .master_agent import MasterAgent
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterAgentAPI:
    """API wrapper for Master Agent"""
    
    def __init__(self, model_name: Optional[str] = None, temperature: Optional[float] = None):
        """
        Initialize the Master Agent API
        
        Args:
            model_name: OpenAI model name (optional)
            temperature: Temperature for LLM (optional)
        """
        self.agent = MasterAgent(model_name=model_name, temperature=temperature)
    
    def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Main API method for chat interactions
        
        Args:
            message: User's message
            conversation_history: Previous conversation history (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            result = self.agent.chat(message, conversation_history)
            return result
        
        except Exception as e:
            logger.error(f"Error in Master Agent API chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def reset(self):
        """
        Reset the agent (for new conversations)
        """
        self.agent.reset()




