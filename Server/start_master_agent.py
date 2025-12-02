#!/usr/bin/env python
"""
Simple script to start the Master Agent server
Run from the Server directory: python start_master_agent.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from master_agent.config import SERVER_HOST, SERVER_PORT
    
    print(f"Starting Master Agent Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Health check: http://localhost:{SERVER_PORT}/health")
    print(f"API docs: http://localhost:{SERVER_PORT}/docs")
    print(f"Chat endpoint: http://localhost:{SERVER_PORT}/chat")
    
    uvicorn.run(
        "master_agent.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )




