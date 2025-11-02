"""
FastAPI Server for Master Agent
Exposes HTTP endpoints for the Chrome extension
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import uvicorn

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS
from .master_agent import MasterAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Master Agent API",
    description="Central orchestration agent for travel insurance queries",
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

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature for response")
    context: Optional[Dict[str, Any]] = Field(None, description="Session context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Which insurance plan is best for skiing in Japan?",
                "temperature": 0.7
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    success: bool
    response: str
    classification: Optional[str] = None
    agents_consulted: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Based on your skiing trip to Japan, I recommend...",
                "classification": "recommendation",
                "agents_consulted": ["predict", "risk"]
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str


# ============================================================================
# Startup and Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize master agent on startup"""
    global master_agent
    logger.info("Initializing Master Agent...")
    master_agent = MasterAgent()
    logger.info("Master Agent initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global master_agent
    if master_agent:
        await master_agent.close()
        logger.info("Master Agent closed")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - returns API information
    """
    return HealthResponse(
        status="healthy",
        service="Master Agent API",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="Master Agent API",
        version="1.0.0"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - processes user queries and routes to appropriate agents
    
    This is the primary endpoint that the Chrome extension calls.
    The master agent orchestrates communication with specialized agents:
    - Classifier Agent: Determines query type
    - Predict Agent: Provides insurance recommendations
    - Risk Agent: Assesses travel risks
    """
    global master_agent
    
    if not master_agent:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    
    logger.info(f"Received chat request: {request.message[:100]}...")
    
    try:
        result = await master_agent.process_query(
            query=request.message,
            context=request.context
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/agents")
async def list_agents():
    """
    List available specialized agents
    """
    return {
        "agents": [
            {
                "name": "classifier",
                "description": "Classifies user queries into types",
                "capabilities": ["comparison", "explanation", "eligibility", "scenario"]
            },
            {
                "name": "predict",
                "description": "Recommends insurance plans based on historical data",
                "capabilities": ["recommendation", "product comparison", "claims analysis"]
            },
            {
                "name": "risk",
                "description": "Assesses travel risks and hazards",
                "capabilities": ["weather", "disasters", "advisories", "destination safety"]
            }
        ],
        "total": 3
    }


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

