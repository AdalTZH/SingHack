#!/usr/bin/env python
"""
Simple script to start the Policy Analyzer server
Run from the Server directory: python start_policy_eligibility_scanner.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from policy_eligibility_scanner.config import SERVER_HOST, SERVER_PORT
    
    print(f"Starting Policy Analyzer Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Health check: http://localhost:{SERVER_PORT}/health")
    print(f"API docs: http://localhost:{SERVER_PORT}/docs")
    
    uvicorn.run(
        "policy_eligibility_scanner.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

