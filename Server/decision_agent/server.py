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

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS
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
    persuasion_message: Optional[str] = Field(None, description="1-liner persuasion message (max 20 words) to display in cursor textbox")
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
                "persuasion_message": "Protect your adventure! Travel insurance = peace of mind ✈️"
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
    3. If yes, generates a catchy persuasion message (max 20 words)
    4. Returns the decision and persuasion message to display in cursor textbox
    
    Args:
        request: Page sync data (URL, title, HTML content)
        
    Returns:
        Decision result with persuasion message for cursor textbox display
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
        
        # If decision is to prompt, generate persuasion message for cursor textbox
        persuasion_message = None
        if decision_result.get('should_prompt', False):
            try:
                # Generate 1-liner persuasion message for cursor textbox
                persuasion_message = decision_agent.generate_persuasion_message(decision_result)
                logger.info(f"Generated persuasion message: {persuasion_message}")
            except Exception as e:
                logger.error(f"Error generating persuasion message: {e}")
                # Generate fallback message if generation fails
                travel_context = decision_result.get('travel_context', 'travel plans')
                if travel_context:
                    context_words = travel_context.split()[:3]
                    context_short = ' '.join(context_words)
                    persuasion_message = f"Protect your {context_short} with travel insurance! ✈️"
                else:
                    persuasion_message = "Secure your trip with travel insurance - peace of mind awaits!"
                logger.warning(f"Using fallback persuasion message: {persuasion_message}")
                decision_result['persuasion_error'] = str(e)
        
        # Safety check: ensure persuasion_message is set if should_prompt is True
        if decision_result.get('should_prompt', False) and not persuasion_message:
            travel_context = decision_result.get('travel_context', 'travel plans')
            if travel_context:
                context_words = travel_context.split()[:3]
                context_short = ' '.join(context_words)
                persuasion_message = f"Protect your {context_short} with travel insurance! ✈️"
            else:
                persuasion_message = "Secure your trip with travel insurance - peace of mind awaits!"
            logger.warning(f"Persuasion message was None but should_prompt=True, using fallback: {persuasion_message}")
        
        # Log the response being sent
        logger.info(f"Returning response: should_prompt={decision_result.get('should_prompt', False)}, persuasion_message={persuasion_message}")
        
        response = PageSyncResponse(
            success=True,
            should_prompt=decision_result.get('should_prompt', False),
            confidence=decision_result.get('confidence', 0.0),
            reasoning=decision_result.get('reasoning', ''),
            is_travel_related=decision_result.get('is_travel_related', False),
            insurance_needed=decision_result.get('insurance_needed', False),
            travel_context=decision_result.get('travel_context'),
            persuasion_message=persuasion_message
        )
        
        # Double-check the response has persuasion_message
        logger.info(f"Response persuasion_message field: {response.persuasion_message}")
        return response
    
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

