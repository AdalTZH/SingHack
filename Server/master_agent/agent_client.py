"""
Agent Client for A2A (Agent-to-Agent) Communication
Handles communication with specialized agents via HTTP/REST
"""
import httpx
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentClient:
    """
    Client for communicating with specialized agents
    Implements A2A (Agent-to-Agent) protocol via REST API
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the agent client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def call_classifier(
        self,
        query: str,
        include_reasoning: bool = True,
        base_url: str = 'http://localhost:8001'
    ) -> Dict[str, Any]:
        """
        Call the Classifier Agent
        
        Args:
            query: User query to classify
            include_reasoning: Whether to include classification reasoning
            base_url: Base URL of the classifier agent service
            
        Returns:
            Classification result
        """
        try:
            # Use MCP server endpoint if running, otherwise try direct API
            url = f"{base_url}/classify"
            
            payload = {
                "query": query,
                "include_reasoning": include_reasoning
            }
            
            logger.info(f"Calling Classifier Agent: {url}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Error calling Classifier Agent: {e}")
            return {
                "success": False,
                "error": f"Classification service unavailable: {str(e)}",
                "classification": "unknown"
            }
    
    async def call_predict(
        self,
        query: str,
        context: Optional[Dict] = None,
        base_url: str = 'http://localhost:8002'
    ) -> Dict[str, Any]:
        """
        Call the Predict Agent
        
        Args:
            query: User query or data
            context: Additional context for prediction
            base_url: Base URL of the predict agent service
            
        Returns:
            Prediction result
        """
        try:
            url = f"{base_url}/predict"
            
            payload = {
                "query": query,
                "context": context or {}
            }
            
            logger.info(f"Calling Predict Agent: {url}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Error calling Predict Agent: {e}")
            return {
                "success": False,
                "error": f"Prediction service unavailable: {str(e)}",
                "recommendations": []
            }
    
    async def call_risk(
        self,
        query: str,
        context: Optional[Dict] = None,
        base_url: str = 'http://localhost:8003'
    ) -> Dict[str, Any]:
        """
        Call the Risk Agent
        
        Args:
            query: User query or risk assessment request
            context: Additional context for risk assessment (can include destination, dates, activities)
            base_url: Base URL of the risk agent service
            
        Returns:
            Risk assessment result
        """
        try:
            url = f"{base_url}/assess_risk"
            
            # Format payload according to RiskAgent API
            payload = {
                "query": query,
                "destination": context.get("destination") if context else None,
                "departure_date": context.get("departure_date") if context else None,
                "return_date": context.get("return_date") if context else None,
                "activities": context.get("activities") if context else None,
                "context": context
            }
            
            logger.info(f"Calling Risk Agent: {url}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Error calling Risk Agent: {e}")
            return {
                "success": False,
                "error": f"Risk assessment service unavailable: {str(e)}",
                "weather_risks": [],
                "natural_disasters": [],
                "travel_advisories": [],
                "activity_risks": [],
                "overall_risk_level": "unknown",
                "recommendations": []
            }


# Convenience function
async def call_agent(agent_type: str, query: str, **kwargs) -> Dict[str, Any]:
    """
    Call a specific agent by type
    
    Args:
        agent_type: Type of agent ('classifier', 'predict', 'risk')
        query: Query or request
        **kwargs: Additional arguments for the agent
        
    Returns:
        Agent response
    """
    client = AgentClient()
    try:
        if agent_type == 'classifier':
            return await client.call_classifier(query, **kwargs)
        elif agent_type == 'predict':
            return await client.call_predict(query, **kwargs)
        elif agent_type == 'risk':
            return await client.call_risk(query, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown agent type: {agent_type}"
            }
    finally:
        await client.close()

