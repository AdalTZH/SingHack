"""
Startup script for Summary Agent server
"""
import sys
import os

# Add Server directory to path
server_dir = os.path.dirname(os.path.abspath(__file__))
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

import uvicorn
from summary_agent.config import SERVER_HOST, SERVER_PORT

if __name__ == "__main__":
    print(f"Starting Summary Agent server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "summary_agent.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True
    )


