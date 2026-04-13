"""
API interface for the Summary Agent
Provides a clean interface for integrating with the summary agent
"""
from .summary_agent import SummaryAgent
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryAgentAPI:
    """API wrapper for Summary Agent"""
    
    def __init__(self):
        self.agent = SummaryAgent()
    
    def summarize_page(self, inner_text: str, url: str, title: str, travel_context: str = "") -> Dict[str, Any]:
        """
        Main API method for summarizing page content
        
        Args:
            inner_text: Page text content
            url: Page URL
            title: Page title
            travel_context: Travel context from Decision Agent (optional)
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            result = self.agent.summarize_page(inner_text, url, title, travel_context)
            return result
        
        except Exception as e:
            logger.error(f"Error in Summary Agent API: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': f"Failed to summarize page",
                'url': url,
                'title': title
            }


