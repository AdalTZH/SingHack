"""
Insights Agent - Determines if analytics should be performed
"""
from openai import OpenAI
import logging
import requests
from typing import Dict, Any, Optional
import json

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE,
    INSIGHTS_ANALYTICS_URL, INSIGHTS_AGENT_SYSTEM_PROMPT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightsAgent:
    """
    Insights Agent that determines if data analytics should be performed
    to provide insights that could convince clients to purchase insurance
    """
    
    def __init__(self, model_name: str = None, temperature: float = None):
        """
        Initialize the Insights Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
            temperature: Temperature for LLM (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.temperature = temperature if temperature is not None else TEMPERATURE
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.analytics_url = INSIGHTS_ANALYTICS_URL
        
        logger.info(f"Insights Agent initialized with model: {self.model_name}")
    
    def should_perform_analytics(self, user_query: str) -> Dict[str, Any]:
        """
        Determine if analytics should be performed for the user query
        
        Args:
            user_query: The user's query/question
            
        Returns:
            Dictionary with:
            - should_analyze: bool - Whether to perform analytics
            - reasoning: str - Why analytics should/shouldn't be performed
            - confidence: float - Confidence level (0.0 to 1.0)
        """
        try:
            prompt = f"""Analyze the following user query and determine if performing data analytics on travel insurance claims data would provide valuable insights that could help convince the user to purchase travel insurance.

User Query: "{user_query}"

Consider:
1. Is this query related to travel risks, destinations, claim statistics, or insurance needs?
2. Would analyzing travel insurance claims data help answer this question?
3. Would the insights from this analysis be persuasive for convincing someone to buy insurance?

Respond with ONLY a JSON object in this exact format:
{{
    "should_analyze": true or false,
    "reasoning": "Brief explanation of your decision",
    "confidence": 0.0 to 1.0
}}

Do not include any other text, just the JSON object."""

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": INSIGHTS_AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            
            logger.info(f"Analytics decision: {result.get('should_analyze')} (confidence: {result.get('confidence', 0.0)})")
            
            return {
                'should_analyze': result.get('should_analyze', False),
                'reasoning': result.get('reasoning', ''),
                'confidence': result.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error determining if analytics should be performed: {e}")
            # Default to not performing analytics on error
            return {
                'should_analyze': False,
                'reasoning': f'Error analyzing query: {str(e)}',
                'confidence': 0.0
            }
    
    def perform_analytics(self, user_query: str) -> Dict[str, Any]:
        """
        Perform analytics using the insights analytics system
        
        Args:
            user_query: The user's query/question
            
        Returns:
            Dictionary with analytics results including:
            - analysis: str - The persuasive insights text
            - query_results: List - Raw query results
            - execution_time: str - Time taken
        """
        try:
            logger.info(f"Performing analytics for query: {user_query}")
            
            response = requests.post(
                f"{self.analytics_url}/query",
                json={'query': user_query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Analytics completed successfully")
                return {
                    'success': True,
                    'analysis': data.get('analysis', ''),
                    'query_results': data.get('query_results', []),
                    'execution_time': data.get('execution_time', ''),
                    'user_query': data.get('user_query', user_query)
                }
            else:
                error_msg = f"Analytics API returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'analysis': None
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to analytics API: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'analysis': None
            }
        except Exception as e:
            error_msg = f"Error performing analytics: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'analysis': None
            }
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query: determine if analytics should be performed,
        and if yes, perform analytics and return insights
        
        Args:
            user_query: The user's query/question
            
        Returns:
            Dictionary with:
            - should_analyze: bool - Whether analytics was recommended
            - performed_analytics: bool - Whether analytics was actually performed
            - insights: str - The insights text (if analytics was performed)
            - reasoning: str - Why analytics was/wasn't performed
            - confidence: float - Confidence in the decision
            - error: str - Error message if something went wrong
        """
        try:
            # Step 1: Determine if analytics should be performed
            decision = self.should_perform_analytics(user_query)
            
            if not decision.get('should_analyze', False):
                return {
                    'should_analyze': False,
                    'performed_analytics': False,
                    'insights': None,
                    'reasoning': decision.get('reasoning', ''),
                    'confidence': decision.get('confidence', 0.0)
                }
            
            # Step 2: Perform analytics
            analytics_result = self.perform_analytics(user_query)
            
            if analytics_result.get('success', False):
                return {
                    'should_analyze': True,
                    'performed_analytics': True,
                    'insights': analytics_result.get('analysis', ''),
                    'reasoning': decision.get('reasoning', ''),
                    'confidence': decision.get('confidence', 0.0),
                    'query_results': analytics_result.get('query_results', []),
                    'execution_time': analytics_result.get('execution_time', '')
                }
            else:
                return {
                    'should_analyze': True,
                    'performed_analytics': False,
                    'insights': None,
                    'reasoning': decision.get('reasoning', ''),
                    'confidence': decision.get('confidence', 0.0),
                    'error': analytics_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'should_analyze': False,
                'performed_analytics': False,
                'insights': None,
                'reasoning': f'Error processing query: {str(e)}',
                'confidence': 0.0,
                'error': str(e)
            }

