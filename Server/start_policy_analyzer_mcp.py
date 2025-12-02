#!/usr/bin/env python
"""
Simple script to start the Policy Analyzer MCP Server
Run from the Server directory: python start_policy_analyzer_mcp.py

Note: This is a standalone MCP server. For chatbot integration,
the tools are automatically loaded by the master agent.
"""
import sys
import os
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    from policy_analyzer_mcp.mcp_server import main
    
    print("Starting Policy Analyzer MCP Server...")
    print("This server provides MCP tools for policy analysis.")
    print("Connect to it using an MCP client.")
    print("-" * 80)
    
    asyncio.run(main())


