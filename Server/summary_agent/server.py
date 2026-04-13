"""
FastAPI server for Summary Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS
from .api import SummaryAgentAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Summary Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*|http://localhost:.*|http://127\.0\.0\.1:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Summary Agent API
summary_api = None


class SummarizeRequest(BaseModel):
    inner_text: str
    url: str
    title: str
    travel_context: Optional[str] = ""


class SummarizeResponse(BaseModel):
    success: bool
    summary: str
    url: str
    title: str
    travel_context: Optional[str] = ""
    metadata: Optional[dict] = None
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the Summary Agent on startup"""
    global summary_api
    try:
        logger.info("Initializing Summary Agent...")
        summary_api = SummaryAgentAPI()
        logger.info("Summary Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Summary Agent: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Summary Agent API",
        "version": "1.0.0"
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_page(request: SummarizeRequest):
    """
    Summarize travel-related page content
    
    Args:
        request: SummarizeRequest with page data
        
    Returns:
        Summary and metadata
    """
    try:
        if not summary_api:
            raise HTTPException(status_code=503, detail="Summary Agent not initialized")
        
        # Validate input
        if not request.inner_text or not request.url or not request.title:
            raise HTTPException(status_code=400, detail="Missing required fields: inner_text, url, or title")
        
        logger.info(f"Received summarization request for: {request.url}")
        
        # Generate summary
        result = summary_api.summarize_page(
            inner_text=request.inner_text,
            url=request.url,
            title=request.title,
            travel_context=request.travel_context or ""
        )
        
        return SummarizeResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing summarization request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Summary Agent server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)


