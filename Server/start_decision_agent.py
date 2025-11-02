#!/usr/bin/env python
"""
Simple script to start the Decision Agent server
Run from the Server directory: python start_decision_agent.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from decision_agent.config import SERVER_HOST, SERVER_PORT
    
    print(f"Starting Decision Agent Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Health check: http://localhost:{SERVER_PORT}/health")
    print(f"API docs: http://localhost:{SERVER_PORT}/docs")
    
    uvicorn.run(
        "decision_agent.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

