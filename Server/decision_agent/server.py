"""
FastAPI Server for Decision Agent
Exposes HTTP endpoints for analyzing page sync data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import uvicorn
import httpx

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS, MASTER_AGENT_URL
from .decision_agent import DecisionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Decision Agent API",
    description="Analyzes page sync data to determine if travel insurance should be offered",
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

# Global decision agent instance
decision_agent = None


# ============================================================================
# Request/Response Models
# ============================================================================

class PageSyncRequest(BaseModel):
    """Request model for page sync analysis"""
    url: str = Field(..., description="Page URL")
    title: str = Field(..., description="Page title")
    html_content: str = Field(..., description="Page HTML/text content")
    timestamp: Optional[str] = Field(None, description="Timestamp of page sync")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/flight-booking",
                "title": "Flight Booking - Example Airlines",
                "html_content": "Book your flight...",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class PageSyncResponse(BaseModel):
    """Response model for page sync analysis"""
    success: bool
    should_prompt: bool = Field(..., description="Whether to prompt user about insurance")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in decision")
    reasoning: str = Field(..., description="Explanation of decision")
    is_travel_related: bool = Field(..., description="Whether page is travel-related")
    insurance_needed: bool = Field(..., description="Whether insurance might be needed")
    travel_context: Optional[str] = Field(None, description="Type of travel activity")
    forwarded_to_master: Optional[bool] = Field(None, description="Whether prompt was forwarded to master agent")
    master_agent_response: Optional[str] = Field(None, description="Response from master agent (to display in chat)")
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "should_prompt": True,
                "confidence": 0.85,
                "reasoning": "User is booking an international flight, which typically requires travel insurance",
                "is_travel_related": True,
                "insurance_needed": True,
                "travel_context": "international flight booking",
                "forwarded_to_master": True,
                "master_agent_response": "Based on your flight booking, I recommend considering travel insurance..."
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
    """Initialize decision agent on startup"""
    global decision_agent
    logger.info("Initializing Decision Agent...")
    decision_agent = DecisionAgent()
    logger.info("Decision Agent initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global decision_agent
    if decision_agent:
        logger.info("Decision Agent shutdown")


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
        service="Decision Agent API",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="Decision Agent API",
        version="1.0.0"
    )


@app.post("/analyze", response_model=PageSyncResponse)
async def analyze_page_sync(request: PageSyncRequest):
    """
    Analyze page sync data to determine if travel insurance should be offered
    
    This endpoint:
    1. Analyzes the page content to determine if it's travel-related
    2. Decides if insurance might be needed
    3. If yes, automatically forwards a prompt to the master agent
    4. Returns the decision and whether it was forwarded
    
    Args:
        request: Page sync data (URL, title, HTML content)
        
    Returns:
        Decision result with forwarding status
    """
    global decision_agent
    
    if not decision_agent:
        raise HTTPException(status_code=503, detail="Decision Agent not initialized")
    
    logger.info(f"Analyzing page sync: {request.title} ({request.url})")
    
    try:
        # Analyze the page
        decision_result = decision_agent.analyze_page(
            url=request.url,
            title=request.title,
            html_content=request.html_content
        )
        
        # If decision is to prompt, forward to master agent
        forwarded = False
        master_agent_response = None
        if decision_result.get('should_prompt', False):
            try:
                # Generate insurance prompt
                insurance_prompt = decision_agent.generate_insurance_prompt(decision_result)
                
                # Forward to master agent
                async with httpx.AsyncClient(timeout=30.0) as client:
                    master_response = await client.post(
                        f"{MASTER_AGENT_URL}/chat",
                        json={
                            "message": insurance_prompt,
                            "context": {
                                "source": "decision_agent",
                                "page_url": request.url,
                                "page_title": request.title,
                                "travel_context": decision_result.get('travel_context', '')
                            }
                        }
                    )
                    
                    if master_response.status_code == 200:
                        forwarded = True
                        master_response_data = master_response.json()
                        master_agent_response = master_response_data.get('response', '')
                        logger.info("Successfully forwarded insurance prompt to master agent")
                        logger.info(f"Master agent response: {master_agent_response[:100]}...")
                    else:
                        logger.warning(f"Master agent returned {master_response.status_code}")
            
            except Exception as e:
                logger.error(f"Error forwarding to master agent: {e}")
                # Don't fail the request if forwarding fails
                decision_result['forwarding_error'] = str(e)
        
        return PageSyncResponse(
            success=True,
            should_prompt=decision_result.get('should_prompt', False),
            confidence=decision_result.get('confidence', 0.0),
            reasoning=decision_result.get('reasoning', ''),
            is_travel_related=decision_result.get('is_travel_related', False),
            insurance_needed=decision_result.get('insurance_needed', False),
            travel_context=decision_result.get('travel_context'),
            forwarded_to_master=forwarded,
            master_agent_response=master_agent_response
        )
    
    except Exception as e:
        logger.error(f"Error analyzing page sync: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Decision Agent Server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "decision_agent.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

