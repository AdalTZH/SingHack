"""
Master Agent - Orchestrates multi-agent workflows using LangGraph
Routes queries to appropriate specialized agents
"""
from typing import Dict, List, Optional, Any, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
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
    messages: Annotated[List[BaseMessage], operator.add]  # Chat history
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
            self._route_to_agent,
            {
                "classify": "call_classifier",
                "predict": "call_predict",
                "risk": "call_risk",
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
        elif any(keyword in query_lower for keyword in ['recommend', 'best plan', 'suitable', 'insurance plan', 'suggest']):
            routing = "predict"
        elif any(keyword in query_lower for keyword in ['risk', 'danger', 'safe', 'advisory', 'disaster', 'natural', 'weather', 'traveling', 'country', 'activity']):
            routing = "risk"
        elif any(keyword in query_lower for keyword in ['explain', 'what', 'how', 'tell me']):
            routing = "explain"
        else:
            routing = "general"
        
        logger.info(f"Routing decision: {routing}")
        
        return {
            'routing_decision': routing
        }
    
    def _route_to_agent(self, state: MasterAgentState) -> str:
        """
        Route to the appropriate agent based on routing decision
        Only classify when NOT suggesting insurance plans (predict), not for risk assessment
        
        Args:
            state: Current state
            
        Returns:
            Next node to visit
        """
        routing = state.get('routing_decision', 'general')
        
        # Route to specific agent based on decision
        if routing == 'predict':
            # For insurance plan suggestions, go directly to predict agent
            return "predict"
        elif routing == 'risk':
            # For risk assessment, go directly to risk agent
            return "risk"
        elif routing in ['compare', 'explain', 'general']:
            # For other queries, use classifier to understand intent
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
        Call the Risk Agent using the API
        
        Args:
            state: Current state
            
        Returns:
            Updated state with risk assessment results
        """
        user_query = state.get('user_query', '')
        logger.info(f"Calling Risk Agent for: {user_query}")
        
        try:
            # Use the risk agent API through agent_client
            # Since agent_client methods are async, we need to handle this in a sync context
            import asyncio
            
            # Try to get the running event loop, or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Call the async agent client method
            risk_result = loop.run_until_complete(
                self.agent_client.call_risk(
                    query=user_query,
                    context=None
                )
            )
            
            logger.info(f"Risk assessment result: {risk_result}")
            
            # Format the response for synthesis
            if risk_result.get('success'):
                result = {
                    'message': f"Risk assessment for travel: {risk_result.get('overall_risk_level', 'unknown')} overall risk level",
                    'overall_risk_level': risk_result.get('overall_risk_level'),
                    'weather_risks': risk_result.get('weather_risks', []),
                    'natural_disasters': risk_result.get('natural_disasters', []),
                    'travel_advisories': risk_result.get('travel_advisories', []),
                    'activity_risks': risk_result.get('activity_risks', []),
                    'recommendations': risk_result.get('recommendations', [])
                }
            else:
                result = {
                    'message': 'Risk assessment service available',
                    'error': risk_result.get('error', 'Unknown error'),
                    'note': 'Risk assessment capabilities via MCP tools'
                }
            
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
                    'error': str(e),
                    'result': {
                        'message': 'Unable to complete risk assessment',
                        'note': 'Service temporarily unavailable'
                    }
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
        messages = state.get('messages', [])
        
        logger.info(f"Synthesizing response from {len(agent_responses)} agent(s) with {len(messages)} previous messages")
        
        # Build message list with chat history
        message_list = [
            SystemMessage(content="You are a helpful travel insurance assistant with access to policy data, risk assessments, and recommendations.")
        ]
        
        # Add previous conversation history
        for msg in messages:
            message_list.append(msg)
        
        # Add the current user query as a natural conversation message
        message_list.append(HumanMessage(content=user_query))
        
        # Build agent context to help synthesize the response
        agent_context = f"""Based on my analysis using specialized agents:

Classification: {classification}

Agent Analysis:"""
        
        for response in agent_responses:
            agent_name = response.get('agent', 'unknown')
            result = response.get('result', {})
            agent_context += f"\n\n{agent_name.upper()} Agent:\n{result}"
        
        try:
            # Include agent context in system message when available
            # This provides context while maintaining natural conversation flow
            if agent_responses:
                final_system = SystemMessage(
                    content=f"""You are a helpful travel insurance assistant with access to policy data, risk assessments, and recommendations.

{agent_context}

Please provide a helpful, clear, and concise response to the user's query based on both the conversation history and the agent analysis above. Maintain context and continuity in your response."""
                )
                message_list_with_context = [final_system] + message_list[1:]  # Replace first system message
            else:
                message_list_with_context = message_list
            
            response = self.llm.invoke(message_list_with_context)
            
            final_response = response.content.strip()
            
            logger.info(f"Generated final response (length: {len(final_response)})")
            
            # Add current user query and assistant response to messages
            new_messages = [
                HumanMessage(content=user_query),
                AIMessage(content=final_response)
            ]
            
            return {
                'final_response': final_response,
                'messages': new_messages
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            # Fallback response
            fallback = f"I received your query: '{user_query}'. I'm currently processing this with multiple specialized agents and will provide you with comprehensive information shortly."
            
            # Add messages even on error
            new_messages = [
                HumanMessage(content=user_query),
                AIMessage(content=fallback)
            ]
            
            return {
                'final_response': fallback,
                'messages': new_messages
            }
    
    async def process_query(self, query: str, context: Optional[Dict] = None, messages: Optional[List[BaseMessage]] = None) -> Dict[str, Any]:
        """
        Main method to process a user query
        
        Args:
            query: User query
            context: Optional session context
            messages: Optional list of previous conversation messages (BaseMessage objects)
            
        Returns:
            Response dictionary
        """
        logger.info(f"Processing query: {query}")
        
        # Convert messages to list if provided, otherwise use empty list
        initial_messages = messages if messages is not None else []
        
        try:
            # Invoke the graph
            result = self.graph.invoke({
                'user_query': query,
                'session_context': context or {},
                'messages': initial_messages,
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
                },
                'messages': result.get('messages', [])  # Return updated messages for next request
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'response': f"I encountered an error processing your query: {str(e)}",
                'error': str(e),
                'messages': initial_messages  # Return messages even on error
            }
    
    async def close(self):
        """Clean up resources"""
        await self.agent_client.close()

