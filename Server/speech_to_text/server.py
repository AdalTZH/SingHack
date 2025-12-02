"""
FastAPI Server for Speech-to-Text
Exposes HTTP endpoints for audio transcription using MERaLiON-2-3B model
Based on testing.py configuration
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn
import base64
import numpy as np
import torch
import io
import wave
import json

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS, REPO_ID, DEVICE, SAMPLE_RATE
from .transcriber import SpeechTranscriber

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Speech-to-Text API",
    description="Audio transcription using MERaLiON-2-3B model",
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

# Global transcriber instance (loaded once on startup)
transcriber: Optional[SpeechTranscriber] = None


# ============================================================================
# Request/Response Models
# ============================================================================

class TranscriptionRequest(BaseModel):
    """Request model for audio transcription"""
    audio_data: str  # Base64 encoded audio data
    format: Optional[str] = "wav"  # Audio format: wav, webm, etc.


class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load model on server startup"""
    global transcriber
    try:
        logger.info("=" * 60)
        logger.info("Loading MERaLiON-2-3B model... (this may take a while)")
        logger.info("=" * 60)
        # Run model loading in executor to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        transcriber = await loop.run_in_executor(None, SpeechTranscriber)
        logger.info("=" * 60)
        logger.info("Model loaded successfully! Ready to transcribe.")
        logger.info(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    global transcriber
    if transcriber:
        transcriber.cleanup()
        transcriber = None


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": transcriber is not None,
        "device": DEVICE
    }


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio from base64 encoded data
    
    Args:
        request: TranscriptionRequest with base64 audio data
        
    Returns:
        TranscriptionResponse with transcribed text
    """
    logger.info("=" * 60)
    logger.info("Transcription request received")
    logger.info(f"Audio data length: {len(request.audio_data) if request.audio_data else 0} characters")
    logger.info(f"Format: {request.format or 'wav'}")
    
    if not transcriber:
        logger.error("Model not loaded!")
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Decode base64 audio
        logger.info("Decoding base64 audio...")
        audio_bytes = base64.b64decode(request.audio_data)
        logger.info(f"Decoded audio size: {len(audio_bytes)} bytes")
        
        # Convert to numpy array
        logger.info(f"Decoding audio format: {request.format or 'wav'}...")
        audio_array = transcriber.decode_audio(audio_bytes, request.format or "wav")
        logger.info(f"Audio array shape: {audio_array.shape}, dtype: {audio_array.dtype}")
        
        # Transcribe
        logger.info("Starting transcription...")
        transcription = transcriber.transcribe(audio_array)
        logger.info(f"Transcription successful: '{transcription}'")
        logger.info("=" * 60)
        
        return TranscriptionResponse(
            success=True,
            text=transcription
        )
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("=" * 60)
        return TranscriptionResponse(
            success=False,
            error=str(e)
        )


@app.post("/transcribe-file", response_model=TranscriptionResponse)
async def transcribe_file(audio_file: UploadFile = File(...)):
    """
    Transcribe audio from uploaded file
    
    Args:
        audio_file: Uploaded audio file
        
    Returns:
        TranscriptionResponse with transcribed text
    """
    if not transcriber:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read audio file
        audio_bytes = await audio_file.read()
        
        # Get format from file extension
        file_format = audio_file.filename.split('.')[-1].lower() if audio_file.filename else "wav"
        
        # Convert to numpy array
        audio_array = transcriber.decode_audio(audio_bytes, file_format)
        
        # Transcribe
        transcription = transcriber.transcribe(audio_array)
        
        return TranscriptionResponse(
            success=True,
            text=transcription
        )
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return TranscriptionResponse(
            success=False,
            error=str(e)
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
    
    logger.info("Initializing Speech-to-Text Server...")
    logger.info(f"Host: {SERVER_HOST}, Port: {SERVER_PORT}")
    
    uvicorn.run(
        app,  # Pass the app directly instead of string
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,  # Disable reload for production (model loading is expensive)
        log_level="info"
    )


if __name__ == "__main__":
    main()

