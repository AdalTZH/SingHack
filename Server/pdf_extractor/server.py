"""
FastAPI Server for PDF Text Extraction
Exposes HTTP endpoints for extracting text from uploaded PDF documents
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn

from .config import (
    SERVER_HOST, 
    SERVER_PORT, 
    ALLOWED_ORIGINS, 
    MAX_FILE_SIZE, 
    ALLOWED_FILE_TYPES,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SUMMARIZE_BY_DEFAULT
)
from .extractor import PDFExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import summarizer (optional - only if OpenAI is configured)
try:
    from .summarizer import PDFSummarizer
    SUMMARIZER_AVAILABLE = True
except ImportError:
    SUMMARIZER_AVAILABLE = False
    logger.warning("PDF Summarizer not available. Install openai package for summarization features.")
except Exception as e:
    SUMMARIZER_AVAILABLE = False
    logger.warning(f"PDF Summarizer initialization failed: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Text Extraction API",
    description="Extract text content from uploaded PDF documents",
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

# Global extractor instance
extractor: Optional[PDFExtractor] = None

# Global summarizer instance (optional)
summarizer: Optional[PDFSummarizer] = None


# ============================================================================
# Request/Response Models
# ============================================================================

class ExtractionResponse(BaseModel):
    """Response model for PDF text extraction"""
    success: bool
    text: Optional[str] = None
    metadata: Optional[dict] = None
    summary: Optional[str] = None  # AI-generated summary
    summary_metadata: Optional[dict] = None  # Summary generation metadata
    error: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None


class SummarizeRequest(BaseModel):
    """Request model for text summarization"""
    text: str
    detail_level: Optional[str] = "detailed"  # "brief", "detailed", "comprehensive"
    structured: Optional[bool] = False  # Return structured summary


class SummarizeResponse(BaseModel):
    """Response model for text summarization"""
    success: bool
    summary: Optional[str] = None
    detail_level: Optional[str] = None
    token_count: Optional[int] = None
    error: Optional[str] = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize extractor and summarizer on server startup"""
    global extractor, summarizer
    try:
        logger.info("=" * 60)
        logger.info("Initializing PDF Text Extractor...")
        logger.info("=" * 60)
        extractor = PDFExtractor()
        logger.info("PDF Extractor initialized successfully!")
        
        # Initialize summarizer if OpenAI API key is available
        if SUMMARIZER_AVAILABLE:
            if OPENAI_API_KEY:
                try:
                    summarizer = PDFSummarizer(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
                    logger.info(f"PDF Summarizer initialized successfully with model: {OPENAI_MODEL}")
                    logger.info("Summarization features are enabled ✓")
                except Exception as e:
                    logger.warning(f"Failed to initialize PDF Summarizer: {e}")
                    logger.warning("Summarization features will be disabled")
                    summarizer = None
            else:
                logger.info("PDF Summarizer not initialized (OPENAI_API_KEY not found in environment)")
                logger.info("Note: Summarization requires OPENAI_API_KEY in .env file or environment")
        else:
            logger.info("PDF Summarizer not available (install openai package: pip install openai)")
        
        logger.info(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Failed to initialize PDF extractor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    global extractor, summarizer
    extractor = None
    summarizer = None
    logger.info("PDF Extractor server shutting down...")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PDF Text Extraction API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "extract": "/extract",
            "extract-with-summary": "/extract?summarize=true",
            "summarize": "/summarize",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "extractor_loaded": extractor is not None,
        "summarizer_loaded": summarizer is not None,
        "summarizer_available": SUMMARIZER_AVAILABLE,
        "openai_configured": bool(OPENAI_API_KEY),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "allowed_file_types": ALLOWED_FILE_TYPES
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/extract", response_model=ExtractionResponse)
async def extract_text_from_pdf(
    pdf_file: UploadFile = File(...),
    summarize: bool = Query(default=False, description="Generate AI summary of extracted text"),
    detail_level: str = Query(default="detailed", description="Summary detail level: brief, detailed, or comprehensive")
):
    """
    Extract text from uploaded PDF file with optional AI-powered summarization
    
    Args:
        pdf_file: Uploaded PDF file
        summarize: Whether to generate an AI summary (default: False)
        detail_level: Level of summary detail - "brief", "detailed", or "comprehensive" (default: "detailed")
        
    Returns:
        ExtractionResponse with extracted text, metadata, and optional summary
    """
    logger.info("=" * 60)
    logger.info("PDF extraction request received")
    logger.info(f"Filename: {pdf_file.filename}")
    logger.info(f"Content type: {pdf_file.content_type}")
    
    if not extractor:
        logger.error("Extractor not initialized!")
        raise HTTPException(status_code=503, detail="Extractor not initialized")
    
    # Validate file type
    if pdf_file.content_type not in ALLOWED_FILE_TYPES:
        error_msg = f"Invalid file type: {pdf_file.content_type}. Only PDF files are allowed."
        logger.error(error_msg)
        return ExtractionResponse(
            success=False,
            error=error_msg,
            file_name=pdf_file.filename
        )
    
    try:
        # Read file content
        logger.info("Reading PDF file...")
        pdf_bytes = await pdf_file.read()
        file_size = len(pdf_bytes)
        
        logger.info(f"File size: {file_size / (1024 * 1024):.2f} MB")
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            error_msg = f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE / (1024 * 1024):.2f} MB)"
            logger.error(error_msg)
            return ExtractionResponse(
                success=False,
                error=error_msg,
                file_name=pdf_file.filename,
                file_size=file_size
            )
        
        if file_size == 0:
            error_msg = "Uploaded file is empty"
            logger.error(error_msg)
            return ExtractionResponse(
                success=False,
                error=error_msg,
                file_name=pdf_file.filename,
                file_size=file_size
            )
        
        # Extract text
        logger.info("Extracting text from PDF...")
        result = extractor.extract_text(pdf_bytes, filename=pdf_file.filename)
        
        # Add file information to result
        result["file_name"] = pdf_file.filename
        result["file_size"] = file_size
        
        if result["success"]:
            text_length = len(result.get("text", ""))
            pages = result.get("metadata", {}).get("pages", 0)
            logger.info(f"Extraction successful!")
            logger.info(f"  - Text length: {text_length} characters")
            logger.info(f"  - Pages: {pages}")
            
            # Generate summary if requested or if configured to do so by default
            should_summarize = summarize or SUMMARIZE_BY_DEFAULT
            if should_summarize and summarizer and result.get("text"):
                logger.info("Generating PDF summary...")
                try:
                    summary_result = summarizer.summarize(
                        text=result["text"],
                        detail_level=detail_level
                    )
                    if summary_result["success"]:
                        result["summary"] = summary_result["summary"]
                        result["summary_metadata"] = {
                            "detail_level": summary_result["detail_level"],
                            "token_count": summary_result.get("token_count"),
                            "summary_length": summary_result.get("summary_length")
                        }
                        logger.info(f"Summary generated successfully ({len(result['summary'])} characters)")
                    else:
                        logger.warning(f"Summary generation failed: {summary_result.get('error')}")
                except Exception as e:
                    logger.error(f"Error generating summary: {e}")
                    # Don't fail the extraction if summary fails
            
            logger.info("=" * 60)
        else:
            logger.warning(f"Extraction failed: {result.get('error', 'Unknown error')}")
            logger.info("=" * 60)
        
        return ExtractionResponse(**result)
        
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        logger.info("=" * 60)
        
        return ExtractionResponse(
            success=False,
            error=error_msg,
            file_name=pdf_file.filename
        )


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Generate an AI-powered summary of provided text
    
    Args:
        request: SummarizeRequest with text and options
        
    Returns:
        SummarizeResponse with generated summary
    """
    logger.info("=" * 60)
    logger.info("Text summarization request received")
    logger.info(f"Text length: {len(request.text)} characters")
    logger.info(f"Detail level: {request.detail_level}")
    logger.info(f"Structured: {request.structured}")
    
    if not summarizer:
        logger.error("Summarizer not initialized!")
        return SummarizeResponse(
            success=False,
            error="Summarizer not available. Please ensure OPENAI_API_KEY is configured."
        )
    
    if not request.text or not request.text.strip():
        return SummarizeResponse(
            success=False,
            error="No text provided for summarization"
        )
    
    try:
        if request.structured:
            logger.info("Generating structured summary...")
            summary_result = summarizer.summarize_with_structure(request.text)
        else:
            logger.info(f"Generating {request.detail_level} summary...")
            summary_result = summarizer.summarize(
                text=request.text,
                detail_level=request.detail_level
            )
        
        if summary_result["success"]:
            logger.info(f"Summary generated successfully ({len(summary_result['summary'])} characters)")
            logger.info("=" * 60)
            return SummarizeResponse(
                success=True,
                summary=summary_result["summary"],
                detail_level=summary_result.get("detail_level", request.detail_level),
                token_count=summary_result.get("token_count")
            )
        else:
            logger.warning(f"Summary generation failed: {summary_result.get('error')}")
            logger.info("=" * 60)
            return SummarizeResponse(
                success=False,
                error=summary_result.get("error", "Unknown error during summarization")
            )
    
    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        logger.info("=" * 60)
        return SummarizeResponse(
            success=False,
            error=error_msg
        )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the server"""
    import sys
    import os
    
    # Ensure we can import the module correctly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    logger.info("Initializing PDF Text Extraction Server...")
    logger.info(f"Host: {SERVER_HOST}, Port: {SERVER_PORT}")
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

