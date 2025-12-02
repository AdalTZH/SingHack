# Policy Analyzer MCP Server

MCP (Model Context Protocol) server that provides tools for policy analysis via API calls to the Policy Analyzer service.

## Overview

This MCP server exposes all Policy Analyzer functions as MCP tools that can be used by chatbots and AI agents. It connects to the Policy Analyzer API (running on port 8006 by default) and provides:

- Policy eligibility scanning
- Benefits listing and details
- Exclusions listing and details
- Policy grading and comparison

## Structure

- `mcp_server.py` - Standalone MCP server (for direct MCP usage)
- `langchain_tools.py` - LangChain tools wrapper (for master agent integration)
- `mcp_client.py` - MCP client wrapper (for programmatic access)
- `config.py` - Configuration settings

## Integration with Master Agent

The master agent automatically loads and binds these tools when available. The tools are integrated via LangChain's tool binding system, allowing the LLM to call policy analysis functions when needed.

### Available Tools

1. **scan_policy_eligibility** - Scan eligibility for a product and user data
2. **show_policy_benefits** - Get list of benefits for product(s)
3. **show_policy_benefit_details** - Get detailed benefit information
4. **show_policy_exclusion** - Get list of exclusions for a product
5. **show_policy_exclusion_details** - Get detailed exclusion information
6. **grade_policy** - Grade and compare policies based on prioritized benefits
7. **get_products** - Get list of available products
8. **get_eligibility_conditions** - Get list of eligibility conditions

## Configuration

Set the following environment variable:
- `POLICY_ANALYZER_API_URL` - URL of the Policy Analyzer API (default: `http://localhost:8006`)

## Usage

### As Standalone MCP Server

```bash
python -m policy_analyzer_mcp.mcp_server
```

### With Master Agent

The master agent automatically loads the tools if the `policy_analyzer_mcp` package is available. The tools are bound to the LLM and can be called automatically when the agent needs policy information.

## Requirements

- `mcp>=1.0.0` - MCP SDK
- `httpx>=0.27.0` - HTTP client
- `langchain-core` - For LangChain tool integration
- Policy Analyzer API must be running on the configured URL


