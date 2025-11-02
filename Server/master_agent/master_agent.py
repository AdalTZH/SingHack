"""
Master Agent - Orchestrates multi-agent workflows using LangGraph
Routes queries to appropriate specialized agents
"""
from typing import Dict, List, Optional, Any, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator
import logging

from .config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE
from .agent_client import AgentClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterAgentState(TypedDict):
    """State schema for the master agent workflow"""
    user_query: str
    session_context: Dict[str, Any]
    agent_responses: Annotated[List[Dict[str, Any]], operator.add]
    classification: Optional[str]
    routing_decision: Optional[str]
    final_response: Optional[str]


class MasterAgent:
    """
    Master Agent that orchestrates communication with specialized agents:
    - Classifier Agent: Determines query type
    - Predict Agent: Provides insurance recommendations
    - Risk Agent: Assesses travel risks
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Master Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=self.model_name,
            temperature=TEMPERATURE
        )
        self.agent_client = AgentClient()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow for master agent orchestration
        
        Returns:
            Compiled StateGraph
        """
        # Create the graph builder
        graph_builder = StateGraph(MasterAgentState)
        
        # Add nodes
        graph_builder.add_node("route_query", self._route_query)
        graph_builder.add_node("call_classifier", self._call_classifier)
        graph_builder.add_node("call_predict", self._call_predict)
        graph_builder.add_node("call_risk", self._call_risk)
        graph_builder.add_node("synthesize_response", self._synthesize_response)
        
        # Define edges
        graph_builder.add_edge(START, "route_query")
        graph_builder.add_conditional_edges(
            "route_query",
            self._should_classify,
            {
                "classify": "call_classifier",
                "direct": "synthesize_response",
                END: END
            }
        )
        graph_builder.add_edge("call_classifier", "synthesize_response")
        graph_builder.add_edge("call_predict", "synthesize_response")
        graph_builder.add_edge("call_risk", "synthesize_response")
        graph_builder.add_edge("synthesize_response", END)
        
        # Compile the graph
        return graph_builder.compile()
    
    def _route_query(self, state: MasterAgentState) -> Dict[str, Any]:
        """
        Route the query to determine which agent(s) to call
        
        Args:
            state: Current state
            
        Returns:
            Updated state with routing decision
        """
        user_query = state.get('user_query', '')
        logger.info(f"Routing query: {user_query}")
        
        # Simple heuristic-based routing
        query_lower = user_query.lower()
        
        # Check for specific patterns
        if any(keyword in query_lower for keyword in ['compare', 'which', 'better', 'difference']):
            routing = "compare"
        elif any(keyword in query_lower for keyword in ['recommend', 'best plan', 'suitable', 'insurance plan']):
            routing = "predict"
        elif any(keyword in query_lower for keyword in ['risk', 'danger', 'safe', 'advisory', 'disaster']):
            routing = "risk"
        elif any(keyword in query_lower for keyword in ['explain', 'what', 'how', 'tell me']):
            routing = "explain"
        else:
            routing = "general"
        
        logger.info(f"Routing decision: {routing}")
        
        return {
            'routing_decision': routing
        }
    
    def _should_classify(self, state: MasterAgentState) -> str:
        """
        Determine if classification is needed
        
        Args:
            state: Current state
            
        Returns:
            Next node to visit
        """
        routing = state.get('routing_decision', 'general')
        
        # Classification needed for compare/explain queries
        if routing in ['compare', 'explain', 'general']:
            return "classify"
        else:
            return "direct"
    
    def _call_classifier(self, state: MasterAgentState) -> Dict[str, Any]:
        """
        Call the Classifier Agent
        
        Args:
            state: Current state
            
        Returns:
            Updated state with classification results
        """
        user_query = state.get('user_query', '')
        logger.info(f"Calling Classifier Agent for: {user_query}")
        
        try:
            # Try to import and use ClassifierAgent directly
            try:
                import sys
                import os
                # Add parent directory to path
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from classifier_agent import ClassifierAgent
                classifier = ClassifierAgent()
                result = classifier.classify(user_query)
            except Exception as import_error:
                logger.warning(f"Direct import failed, using fallback: {import_error}")
                # Fallback to mock response
                result = {
                    'classification': 'general',
                    'confidence': 0.5,
                    'reasoning': 'Using fallback classification'
                }
            
            logger.info(f"Classification result: {result}")
            
            return {
                'classification': result.get('classification', 'general'),
                'agent_responses': [{
                    'agent': 'classifier',
                    'result': result
                }]
            }
        
        except Exception as e:
            logger.error(f"Error calling Classifier Agent: {e}")
            return {
                'classification': 'general',
                'agent_responses': [{
                    'agent': 'classifier',
                    'error': str(e)
                }]
            }
    
    def _call_predict(self, state: MasterAgentState) -> Dict[str, Any]:
        """
        Call the Predict Agent
        
        Args:
            state: Current state
            
        Returns:
            Updated state with prediction results
        """
        user_query = state.get('user_query', '')
        logger.info(f"Calling Predict Agent for: {user_query}")
        
        try:
            # Import locally to avoid circular dependencies
            from predict_agent import PredictAgentAPI
            
            predict_api = PredictAgentAPI()
            
            # For now, return a placeholder response
            # In production, this would extract user data and call predict
            result = {
                'message': 'Predict Agent: Insurance plan recommendations based on historical data.',
                'recommendations': []
            }
            
            logger.info(f"Prediction result: {result}")
            
            return {
                'agent_responses': [{
                    'agent': 'predict',
                    'result': result
                }]
            }
        
        except Exception as e:
            logger.error(f"Error calling Predict Agent: {e}")
            return {
                'agent_responses': [{
                    'agent': 'predict',
                    'error': str(e)
                }]
            }
    
    def _call_risk(self, state: MasterAgentState) -> Dict[str, Any]:
        """
        Call the Risk Agent
        
        Args:
            state: Current state
            
        Returns:
            Updated state with risk assessment results
        """
        user_query = state.get('user_query', '')
        logger.info(f"Calling Risk Agent for: {user_query}")
        
        try:
            # Risk Agent is MCP-based, return placeholder for now
            # In production, this would use the MCP tools or API
            result = {
                'message': 'Risk Agent: Travel risk assessment based on location and dates.',
                'risks': [],
                'note': 'Risk assessment capabilities available via MCP tools'
            }
            
            logger.info(f"Risk assessment result: {result}")
            
            return {
                'agent_responses': [{
                    'agent': 'risk',
                    'result': result
                }]
            }
        
        except Exception as e:
            logger.error(f"Error calling Risk Agent: {e}")
            return {
                'agent_responses': [{
                    'agent': 'risk',
                    'error': str(e)
                }]
            }
    
    def _synthesize_response(self, state: MasterAgentState) -> Dict[str, Any]:
        """
        Synthesize the final response from agent results
        
        Args:
            state: Current state
            
        Returns:
            Updated state with final response
        """
        user_query = state.get('user_query', '')
        agent_responses = state.get('agent_responses', [])
        classification = state.get('classification', 'general')
        
        logger.info(f"Synthesizing response from {len(agent_responses)} agent(s)")
        
        # Use LLM to synthesize a coherent response
        synthesis_prompt = f"""You are an AI insurance assistant helping users with travel insurance questions.

User Query: "{user_query}"
Classification: {classification}

Agent Responses:"""
        
        for response in agent_responses:
            agent_name = response.get('agent', 'unknown')
            result = response.get('result', {})
            synthesis_prompt += f"\n\n{agent_name.upper()} Agent:\n{result}"
        
        synthesis_prompt += f"""

Please provide a helpful, clear, and concise response to the user's query based on the information above."""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a helpful travel insurance assistant with access to policy data, risk assessments, and recommendations."),
                HumanMessage(content=synthesis_prompt)
            ])
            
            final_response = response.content.strip()
            
            logger.info(f"Generated final response (length: {len(final_response)})")
            
            return {
                'final_response': final_response
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            # Fallback response
            fallback = f"I received your query: '{user_query}'. I'm currently processing this with multiple specialized agents and will provide you with comprehensive information shortly."
            return {
                'final_response': fallback
            }
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main method to process a user query
        
        Args:
            query: User query
            context: Optional session context
            
        Returns:
            Response dictionary
        """
        logger.info(f"Processing query: {query}")
        
        try:
            # Invoke the graph
            result = self.graph.invoke({
                'user_query': query,
                'session_context': context or {},
                'agent_responses': [],
                'classification': None,
                'routing_decision': None,
                'final_response': None
            })
            
            return {
                'success': True,
                'response': result['final_response'],
                'classification': result.get('classification'),
                'agents_consulted': [r.get('agent') for r in result.get('agent_responses', [])],
                'metadata': {
                    'routing_decision': result.get('routing_decision')
                }
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'response': f"I encountered an error processing your query: {str(e)}",
                'error': str(e)
            }
    
    async def close(self):
        """Clean up resources"""
        await self.agent_client.close()

