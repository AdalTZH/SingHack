"""
API interface for the Decision Agent
Provides a clean interface for integrating with the decision agent
"""
from .decision_agent import DecisionAgent
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionAgentAPI:
    """API wrapper for Decision Agent"""
    
    def __init__(self):
        self.agent = DecisionAgent()
    
    def analyze_page_sync(self, url: str, title: str, html_content: str) -> Dict[str, Any]:
        """
        Main API method for analyzing page sync data
        
        Args:
            url: Page URL
            title: Page title
            html_content: Page HTML/text content
            
        Returns:
            Dictionary with decision results
        """
        try:
            result = self.agent.analyze_page(url, title, html_content)
            result['success'] = True
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing page sync data: {e}")
            return {
                'success': False,
                'error': str(e),
                'should_prompt': False,
                'confidence': 0.0,
                'reasoning': f'Error during analysis: {str(e)}'
            }
    
    def should_prompt_insurance(self, url: str, title: str, html_content: str) -> bool:
        """
        Simple boolean check if insurance should be prompted
        
        Args:
            url: Page URL
            title: Page title
            html_content: Page HTML/text content
            
        Returns:
            True if user should be prompted about insurance
        """
        try:
            result = self.agent.analyze_page(url, title, html_content)
            return result.get('should_prompt', False)
        except Exception as e:
            logger.error(f"Error in should_prompt_insurance: {e}")
            return False

