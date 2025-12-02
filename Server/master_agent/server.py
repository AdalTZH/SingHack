"""
FastAPI Server for Master Agent (Insurance Agent)
Exposes HTTP endpoints for chat interface
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import uvicorn
import base64
import io

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS, OPENAI_API_KEY
from .master_agent import MasterAgent
import requests
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Master Agent API",
    description="Insurance Agent powered by LangGraph and GPT",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global master agent instance
master_agent = None


# ============================================================================
# Request/Response Models
# ============================================================================

class DocumentSummary(BaseModel):
    """Model for document summary"""
    file_name: str = Field(..., description="Name of the uploaded file")
    summary: Optional[str] = Field(None, description="AI-generated summary of the document")
    text: Optional[str] = Field(None, description="Extracted text from the document")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata (pages, etc.)")


class ChatMessage(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User's message")
    temperature: Optional[float] = Field(None, description="Temperature for response generation")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Previous conversation history"
    )
    document_summaries: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of document summaries from uploaded PDFs. Each should have file_name, summary, text, and metadata."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What does travel insurance cover?",
                "temperature": 0.7,
                "conversation_history": [],
                "document_summaries": [
                    {
                        "file_name": "policy.pdf",
                        "summary": "This document outlines travel insurance policy details...",
                        "text": "Full extracted text...",
                        "metadata": {"pages": 5}
                    }
                ]
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    success: bool
    response: Optional[str] = Field(None, description="Agent's response")
    error: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Updated conversation history"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )
    insights: Optional[str] = Field(
        None,
        description="Dynamic insights from analytics (if available)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Travel insurance typically covers trip cancellation, medical emergencies, baggage loss, and more...",
                "conversation_history": [
                    {
                        "user": "What does travel insurance cover?",
                        "assistant": "Travel insurance typically covers..."
                    }
                ],
                "metadata": {
                    "model": "gpt-4o",
                    "iterations": 1
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    model: Optional[str] = None


class SpeechToTextRequest(BaseModel):
    """Request model for speech-to-text"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    format: Optional[str] = Field("webm", description="Audio format (webm, wav, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "base64_encoded_audio_string",
                "format": "webm"
            }
        }


class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text"""
    success: bool
    text: Optional[str] = Field(None, description="Transcribed text")
    error: Optional[str] = None


# ============================================================================
# Startup and Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize master agent on startup"""
    global master_agent
    logger.info("Initializing Master Agent...")
    try:
        master_agent = MasterAgent()
        logger.info("Master Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Master Agent: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global master_agent
    if master_agent:
        logger.info("Master Agent shutdown")
        master_agent = None


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - returns API information
    """
    global master_agent
    return HealthResponse(
        status="healthy",
        service="Master Agent API",
        version="1.0.0",
        model=master_agent.model_name if master_agent else None
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    global master_agent
    return HealthResponse(
        status="healthy" if master_agent else "initializing",
        service="Master Agent API",
        version="1.0.0",
        model=master_agent.model_name if master_agent else None
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Chat endpoint for insurance agent
    
    Receives user messages and returns insurance agent responses.
    Supports conversation history for multi-turn conversations.
    
    Args:
        request: Chat message with optional conversation history
        
    Returns:
        Agent response with updated conversation history
    """
    global master_agent
    
    if not master_agent:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    
    # Print to terminal with clear formatting
    print("\n" + "="*80)
    print("📨 MASTER AGENT - INCOMING REQUEST")
    print("="*80)
    print(f"👤 User Message: {request.message}")
    if request.temperature:
        print(f"🌡️  Temperature: {request.temperature}")
    if request.conversation_history:
        print(f"💬 Conversation History: {len(request.conversation_history)} previous messages")
    if request.document_summaries:
        print(f"📄 Document Summaries: {len(request.document_summaries)} document(s) available")
        for idx, doc in enumerate(request.document_summaries, 1):
            print(f"   Document {idx}: {doc.get('file_name', 'Unknown')}")
            print(f"   - Has summary: {bool(doc.get('summary'))}")
            print(f"   - Has text: {bool(doc.get('text'))}")
            if doc.get('summary'):
                print(f"   - Summary length: {len(doc.get('summary', ''))} chars")
    else:
        print("📄 Document Summaries: None provided")
    print("-"*80)
    
    logger.info(f"Received chat message: {request.message[:100]}...")
    
    try:
        # Use custom temperature if provided
        agent = master_agent
        if request.temperature is not None:
            # Create a temporary agent with custom temperature
            from .master_agent import MasterAgent
            agent = MasterAgent(temperature=request.temperature)
        
        # Process the chat message with document summaries
        result = agent.chat(
            message=request.message,
            conversation_history=request.conversation_history,
            document_summaries=request.document_summaries
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error occurred")
            )
        
        response_text = result.get('response', '')
        
        # Note: Insights are now handled separately by the frontend
        # The Insights Agent runs independently and the frontend combines both responses
        
        # Print full response to terminal
        print("\n🤖 MASTER AGENT - RESPONSE")
        print("-"*80)
        print(response_text)
        print("="*80 + "\n")
        
        logger.info(f"Generated response: {response_text[:100]}...")
        
        return ChatResponse(
            success=True,
            response=result.get("response"),
            conversation_history=result.get("conversation_history"),
            metadata=result.get("metadata"),
            insights=None  # Insights handled separately by frontend
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(request: SpeechToTextRequest):
    """
    Speech-to-text endpoint for converting audio to text
    
    Uses OpenAI Whisper API for transcription.
    
    Args:
        request: Audio data and format
        
    Returns:
        Transcribed text
    """
    try:
        # Decode base64 audio data
        try:
            audio_bytes = base64.b64decode(request.audio_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 audio data: {str(e)}"
            )
        
        # Use OpenAI Whisper API for transcription
        try:
            from openai import OpenAI
            
            if not OPENAI_API_KEY:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured"
                )
            
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{request.format or 'webm'}"
            
            # Transcribe using Whisper
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            logger.info(f"Speech-to-text transcription successful")
            
            return SpeechToTextResponse(
                success=True,
                text=transcript
            )
        
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="OpenAI library not installed. Install with: pip install openai"
            )
        except Exception as e:
            logger.error(f"Error in speech-to-text transcription: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Transcription error: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing speech-to-text request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Master Agent Server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "master_agent.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

