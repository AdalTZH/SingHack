"""
Risk Agent Server - Entry point for running the API server
"""
import uvicorn
import logging
from .config import RISK_ASSESSMENT_SETTINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for running the server"""
    logger.info("Starting Risk Agent API server...")
    logger.info(f"Risk assessment settings: {RISK_ASSESSMENT_SETTINGS}")
    
    uvicorn.run(
        "risk_agent.api:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

