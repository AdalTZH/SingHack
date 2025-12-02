#!/usr/bin/env python
"""
Simple script to start the Quotation API server
Run from the Server directory: python start_quotation_api.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from quotation_api.config import SERVER_HOST, SERVER_PORT
    
    print(f"Starting Quotation API Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Health check: http://localhost:{SERVER_PORT}/health")
    print(f"API docs: http://localhost:{SERVER_PORT}/docs")
    print(f"Quote endpoint: http://localhost:{SERVER_PORT}/quote")
    
    uvicorn.run(
        "quotation_api.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

