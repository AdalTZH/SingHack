"""
Master Agent - Insurance Agent using LangGraph
Implements a conversational insurance agent with state management
"""
from typing import Dict, Any, List, TypedDict, Annotated, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS,
    INSURANCE_AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
)

# Import policy analyzer tools
try:
    import sys
    import os
    # Add policy_analyzer_mcp to path
    policy_mcp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'policy_analyzer_mcp')
    if policy_mcp_path not in sys.path:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from policy_analyzer_mcp.langchain_tools import get_policy_analyzer_tools
    POLICY_TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Policy Analyzer tools not available: {e}")
    POLICY_TOOLS_AVAILABLE = False

# Import quotation tools
try:
    from .quotation_tools import get_quotation_tools
    QUOTATION_TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Quotation tools not available: {e}")
    QUOTATION_TOOLS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the insurance agent conversation
    
    - messages: Stores full chat history using LangGraph's add_messages reducer
                All HumanMessage, AIMessage, SystemMessage, and ToolMessage objects
                are accumulated here across the conversation
    - conversation_history: Derived summary format for external API compatibility
    - iteration_count: Number of agent iterations in current workflow run
    - document_summaries: List of document summaries from uploaded PDFs
    """
    messages: Annotated[List[BaseMessage], add_messages]
    conversation_history: List[Dict[str, str]]
    iteration_count: int
    document_summaries: Optional[List[Dict[str, Any]]]


class MasterAgent:
    """
    Master Insurance Agent using LangGraph
    
    This agent:
    1. Maintains conversation state
    2. Processes user messages
    3. Generates insurance-related responses
    4. Manages conversation flow
    """
    
    def __init__(self, model_name: str = None, temperature: float = None):
        """
        Initialize the Master Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
            temperature: Temperature for LLM (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.temperature = temperature if temperature is not None else TEMPERATURE
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=MAX_TOKENS
        )
        
        # Bind policy analyzer tools and quotation tools if available
        all_tools = []
        
        if POLICY_TOOLS_AVAILABLE:
            try:
                policy_tools = get_policy_analyzer_tools()
                all_tools.extend(policy_tools)
                logger.info(f"Loaded {len(policy_tools)} policy analyzer tools")
            except Exception as e:
                logger.warning(f"Failed to load policy tools: {e}")
        
        if QUOTATION_TOOLS_AVAILABLE:
            try:
                quotation_tools = get_quotation_tools()
                all_tools.extend(quotation_tools)
                logger.info(f"Loaded {len(quotation_tools)} quotation tools")
            except Exception as e:
                logger.warning(f"Failed to load quotation tools: {e}")
        
        # Bind all tools to LLM
        if all_tools:
            try:
                self.llm = self.llm.bind_tools(all_tools)
                logger.info(f"Bound {len(all_tools)} total tools to LLM")
            except Exception as e:
                logger.warning(f"Failed to bind tools: {e}")
                self.llm = ChatOpenAI(
                    api_key=OPENAI_API_KEY,
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=MAX_TOKENS
                )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info(f"Master Agent initialized with model: {self.model_name}")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for the insurance agent
        
        Returns:
            StateGraph workflow
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("check_iterations", self._check_iterations_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add edges
        workflow.add_edge("agent", "check_iterations")
        workflow.add_conditional_edges(
            "check_iterations",
            self._should_continue,
            {
                "continue": "agent",
                "end": END
            }
        )
        
        return workflow
    
    def _build_system_prompt(self, document_summaries: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Build system prompt with optional document context
        
        Args:
            document_summaries: List of document summaries from uploaded PDFs
            
        Returns:
            Enhanced system prompt with document context
        """
        system_prompt = INSURANCE_AGENT_SYSTEM_PROMPT
        
        # Add document context if summaries are available
        if document_summaries and len(document_summaries) > 0:
            document_context = "\n\n=== UPLOADED DOCUMENTS ===\n"
            document_context += "The user has uploaded the following documents. Use this information to answer questions about their insurance documents, policy details, coverage, claims, or any information contained in these documents:\n\n"
            
            for idx, doc_summary in enumerate(document_summaries, 1):
                file_name = doc_summary.get('file_name', f'Document {idx}')
                summary = doc_summary.get('summary', '')
                pages = doc_summary.get('metadata', {}).get('pages', 'unknown')
                
                document_context += f"Document {idx}: {file_name} ({pages} pages)\n"
                document_context += f"Summary: {summary}\n\n"
                
                # Add extracted text if available (truncated for context)
                extracted_text = doc_summary.get('text', '')
                if extracted_text:
                    # Include first 500 characters of extracted text for reference
                    text_preview = extracted_text[:500] + ('...' if len(extracted_text) > 500 else '')
                    document_context += f"Text Preview: {text_preview}\n\n"
            
            document_context += "When answering questions:\n"
            document_context += "- Reference specific details from these documents when relevant\n"
            document_context += "- Compare information in documents with available insurance products\n"
            document_context += "- Help users understand what their current documents cover\n"
            document_context += "- Suggest improvements or additional coverage if needed\n"
            
            system_prompt = system_prompt + document_context
        
        return system_prompt
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """
        Agent node that processes messages and generates responses
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with agent response
        """
        try:
            # Get messages from state (add_messages reducer handles merging)
            messages = state.get("messages", [])
            
            # Get document summaries from state
            document_summaries = state.get("document_summaries")
            
            # Get the last user message for logging
            last_user_msg = None
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    last_user_msg = msg.content
                    break
            
            if last_user_msg:
                print(f"🔄 Processing in LangGraph agent node...")
                print(f"📝 User input: {last_user_msg[:100]}...")
                if document_summaries:
                    print(f"📄 Document summaries available: {len(document_summaries)} document(s)")
            
            # Build system prompt with document context
            system_prompt = self._build_system_prompt(document_summaries)
            
            # Prepare messages for LLM (include enhanced system prompt)
            llm_messages = [SystemMessage(content=system_prompt)]
            llm_messages.extend(messages)
            
            # Generate response (may include tool calls)
            print(f"🤖 Calling GPT model ({self.model_name})...")
            response = self.llm.invoke(llm_messages)
            print(f"✅ GPT response received ({len(response.content)} characters)")
            
            # Handle tool calls if present
            if hasattr(response, 'tool_calls') and response.tool_calls and len(response.tool_calls) > 0:
                print(f"🔧 Processing {len(response.tool_calls)} tool call(s)...")
                tool_messages = []
                
                # Build tools dictionary from all available tools
                tools_dict = {}
                
                if POLICY_TOOLS_AVAILABLE:
                    try:
                        from policy_analyzer_mcp.langchain_tools import get_policy_analyzer_tools
                        policy_tools = get_policy_analyzer_tools()
                        tools_dict.update({tool.name: tool for tool in policy_tools})
                    except Exception as e:
                        logger.warning(f"Failed to load policy tools for execution: {e}")
                
                if QUOTATION_TOOLS_AVAILABLE:
                    try:
                        from .quotation_tools import get_quotation_tools
                        quotation_tools = get_quotation_tools()
                        tools_dict.update({tool.name: tool for tool in quotation_tools})
                    except Exception as e:
                        logger.warning(f"Failed to load quotation tools for execution: {e}")
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get('name', '')
                    tool_args = tool_call.get('args', {})
                    tool_call_id = tool_call.get('id', '')
                    
                    print(f"  → Calling tool: {tool_name} with args: {tool_args}")
                    
                    if tool_name in tools_dict:
                        try:
                            # Execute tool
                            tool_func = tools_dict[tool_name]
                            # Handle both sync and async tools
                            import inspect
                            import asyncio
                            
                            # Execute tool (synchronous)
                            tool_result = tool_func.invoke(tool_args)
                            
                            tool_messages.append(ToolMessage(
                                content=str(tool_result),
                                tool_call_id=tool_call_id
                            ))
                            print(f"  ✅ Tool {tool_name} completed")
                        except Exception as e:
                            error_msg = f"Error executing {tool_name}: {str(e)}"
                            logger.error(error_msg)
                            tool_messages.append(ToolMessage(
                                content=error_msg,
                                tool_call_id=tool_call_id
                            ))
                    else:
                        error_msg = f"Unknown tool: {tool_name}"
                        tool_messages.append(ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call_id
                        ))
                
                # Add tool messages and get final response
                if tool_messages:
                    llm_messages.append(response)
                    llm_messages.extend(tool_messages)
                    print(f"🔄 Getting final response after tool execution...")
                    response = self.llm.invoke(llm_messages)
                    print(f"✅ Final response received ({len(response.content)} characters)")
            
            # Update conversation history from messages (ensure it's synced with chat history)
            conversation_history = self._extract_conversation_history_from_messages(messages + [response])
            
            # Return state update - add_messages reducer will merge the new message
            return {
                "messages": [response],  # add_messages will merge this with existing messages
                "conversation_history": conversation_history,
                "iteration_count": state.get("iteration_count", 0) + 1,
                "document_summaries": state.get("document_summaries")  # Preserve document summaries
            }
        
        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            # Return error response
            error_message = AIMessage(content=f"I apologize, but I encountered an error. Please try again. Error: {str(e)}")
            # Update conversation history from messages including error
            messages = state.get("messages", [])
            conversation_history = self._extract_conversation_history_from_messages(messages + [error_message])
            return {
                "messages": [error_message],  # add_messages will merge this
                "conversation_history": conversation_history,
                "iteration_count": state.get("iteration_count", 0) + 1,
                "document_summaries": state.get("document_summaries")  # Preserve document summaries
            }
    
    def _check_iterations_node(self, state: AgentState) -> AgentState:
        """
        Check if we've exceeded max iterations
        
        Args:
            state: Current agent state
            
        Returns:
            State (unchanged, just for checking)
        """
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= MAX_ITERATIONS:
            logger.warning(f"Max iterations ({MAX_ITERATIONS}) reached")
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        """
        Determine if conversation should continue
        
        Args:
            state: Current agent state
            
        Returns:
            "continue" or "end"
        """
        iteration_count = state.get("iteration_count", 0)
        
        # End if max iterations reached
        if iteration_count >= MAX_ITERATIONS:
            return "end"
        
        # For now, always end after one response (single-turn)
        # Can be modified for multi-turn conversations
        return "end"
    
    def _extract_conversation_history_from_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """
        Extract conversation history in simplified format from messages
        
        This method converts the full message history stored in the LangGraph state
        into a simplified format for external API compatibility. It extracts only
        HumanMessage and AIMessage pairs, filtering out SystemMessage, ToolMessage,
        and intermediate tool call messages.
        
        Args:
            messages: List of BaseMessage objects from LangGraph state
            
        Returns:
            List of dictionaries with 'user' and 'assistant' keys
        """
        conversation_history = []
        current_pair = {}
        
        for msg in messages:
            # Skip system messages, tool messages, and other non-conversational messages
            if isinstance(msg, (SystemMessage, ToolMessage)):
                continue
            
            if isinstance(msg, HumanMessage):
                # If we have an unpaired assistant message, save it first
                if 'assistant' in current_pair and 'user' not in current_pair:
                    conversation_history.append({
                        'user': '',
                        'assistant': current_pair['assistant']
                    })
                    current_pair = {}
                # Start a new pair with user message
                current_pair = {'user': msg.content}
            
            elif isinstance(msg, AIMessage):
                # Check if this is a tool call message (skip intermediate tool calls)
                tool_calls = getattr(msg, 'tool_calls', None)
                if tool_calls and len(tool_calls) > 0:
                    # Skip tool call messages in conversation history
                    # We only want the final response after tool execution
                    continue
                
                # Complete the pair with assistant message
                if 'user' in current_pair:
                    current_pair['assistant'] = msg.content
                    conversation_history.append(current_pair)
                    current_pair = {}
                else:
                    # Orphaned assistant message (shouldn't happen, but handle gracefully)
                    current_pair['assistant'] = msg.content
        
        # Handle any remaining unpaired messages
        if current_pair:
            if 'user' in current_pair and 'assistant' not in current_pair:
                # Unpaired user message - this might happen mid-conversation
                # Don't add incomplete pairs
                pass
            elif 'assistant' in current_pair:
                conversation_history.append({
                    'user': '',
                    'assistant': current_pair['assistant']
                })
        
        return conversation_history
    
    def chat(self, message: str, conversation_history: List[Dict[str, str]] = None, document_summaries: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Process a chat message and generate a response
        
        Chat history is stored in the LangGraph state's 'messages' field using
        the add_messages reducer. All messages (HumanMessage, AIMessage, etc.)
        are accumulated and maintained in the state across the workflow.
        
        Args:
            message: User's message
            conversation_history: Previous conversation history (optional)
                                 This will be converted to messages and added to state
            document_summaries: List of document summaries from uploaded PDFs (optional)
                               Each summary should have: file_name, summary, text, metadata
            
        Returns:
            Dictionary with response and metadata including updated conversation history
        """
        try:
            # Prepare initial state with chat history
            messages = []
            
            # Add conversation history if provided (convert to messages format)
            # This reconstructs the message history from the simplified format
            if conversation_history:
                for entry in conversation_history:
                    if "user" in entry and entry["user"]:
                        messages.append(HumanMessage(content=entry["user"]))
                    if "assistant" in entry and entry["assistant"]:
                        messages.append(AIMessage(content=entry["assistant"]))
            
            # Add the current user message
            messages.append(HumanMessage(content=message))
            
            # Initialize state with messages - LangGraph's add_messages reducer will handle merging
            initial_state: AgentState = {
                "messages": messages,  # Full chat history stored here
                "conversation_history": conversation_history or [],
                "iteration_count": 0,
                "document_summaries": document_summaries or []  # Include document summaries
            }
            
            # Log document summaries for debugging
            if document_summaries:
                print(f"📄 Initializing state with {len(document_summaries)} document summary(ies)")
                for idx, doc in enumerate(document_summaries, 1):
                    print(f"   Doc {idx}: {doc.get('file_name', 'Unknown')} - Summary: {bool(doc.get('summary'))}, Text: {bool(doc.get('text'))}")
            else:
                print("📄 No document summaries provided in chat request")
            
            # Run the workflow - messages will be accumulated via add_messages reducer
            result = self.app.invoke(initial_state)
            
            # Get all messages from state (includes full chat history)
            all_messages = result.get("messages", [])
            
            # Extract the last AI message for response
            ai_messages = [msg for msg in all_messages if isinstance(msg, AIMessage)]
            
            if not ai_messages:
                raise ValueError("No AI response generated")
            
            response_text = ai_messages[-1].content
            
            # Get updated conversation history from state (should be synced with messages)
            updated_conversation_history = result.get("conversation_history", [])
            
            # Ensure conversation_history is derived from messages for consistency
            # This ensures the history format matches what's actually in the state
            if all_messages:
                updated_conversation_history = self._extract_conversation_history_from_messages(all_messages)
            
            # Log to terminal
            print(f"✅ LangGraph workflow completed successfully")
            print(f"📊 Iterations: {result.get('iteration_count', 0)}")
            print(f"💬 Total messages in state: {len(all_messages)}")
            print(f"📝 Conversation history entries: {len(updated_conversation_history)}")
            print(f"🤖 Model: {self.model_name}")
            
            return {
                "success": True,
                "response": response_text,
                "conversation_history": updated_conversation_history,  # Synced with messages
                "metadata": {
                    "model": self.model_name,
                    "iterations": result.get("iteration_count", 0),
                    "total_messages": len(all_messages)  # Show chat history is stored
                }
            }
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def reset(self):
        """
        Reset the agent state (for new conversations)
        """
        logger.info("Master Agent reset")
        # The state is managed per conversation, so this is mainly for logging

