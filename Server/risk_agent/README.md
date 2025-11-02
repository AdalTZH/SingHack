# Risk Agent MCP Server

An MCP (Model Context Protocol) server that exposes tools for travel risk assessment. The server provides tools for checking weather forecasts, natural disasters, and performing web searches for travel risks.

## Tools Provided

### Weather Tools

1. **get_weather_forecast** - Get weather forecast for a location (current conditions + 5-day forecast)
2. **check_severe_weather** - Check for severe weather conditions during travel dates (thunderstorms, heavy rain, high winds, extreme temperatures)

### Disaster Tools

3. **check_natural_disasters** - Check for natural disaster alerts (earthquakes, tsunamis, typhoons, floods, volcanoes, wildfires) using GDACS

### Web Search Tools

4. **web_search_risks** - Search the web for travel risks and warnings using Tavily
5. **comprehensive_risk_search** - Perform comprehensive risk search across multiple categories (weather, disasters, advisories, general safety)
6. **check_travel_advisories** - Check for government travel advisories and warnings (US State Department, UK FCO, etc.)

## Setup

### 1. Install Dependencies

```bash
pip install fastmcp tavily-python requests python-dotenv python-dateutil
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
GDACS_ENABLED=true
```

Or set environment variables directly.

### 3. Configure MCP Server in Cursor

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "RiskAgentServer": {
      "command": "python",
      "args": ["-m", "risk_agent.mcp_server"],
      "cwd": "/path/to/singhacks"
    }
  }
}
```

**Note:** Replace `/path/to/singhacks` with the absolute path to your project directory.

Alternatively, if using a virtual environment:

```json
{
  "mcpServers": {
    "RiskAgentServer": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "risk_agent.mcp_server"],
      "cwd": "/path/to/singhacks"
    }
  }
}
```

## Usage

### Running the Server

The server runs automatically when Cursor starts (if configured in `mcp.json`). The agent can then call the tools directly.

### Testing Tools Manually

You can test the tools programmatically:

```python
from risk_agent.mcp_server import (
    _get_weather_forecast_impl,
    _check_severe_weather_impl,
    _check_natural_disasters_impl,
    _web_search_risks_impl,
    _comprehensive_risk_search_impl
)

# Get weather forecast
forecast = _get_weather_forecast_impl("Tokyo, Japan", "2025-03-15", "2025-03-25")

# Check severe weather
severe_weather = _check_severe_weather_impl("Tokyo, Japan", "2025-03-15", "2025-03-25")

# Check natural disasters
disasters = _check_natural_disasters_impl("Tokyo, Japan", "2025-03-15", "2025-03-25")

# Web search for risks
search_results = _web_search_risks_impl("Tokyo Japan travel risks March 2025")

# Comprehensive search
comprehensive = _comprehensive_risk_search_impl(
    destination="Tokyo, Japan",
    departure_date="2025-03-15",
    activities=["hiking", "sightseeing"]
)
```

## Tool Descriptions

### get_weather_forecast

Get weather forecast for a location with optional travel dates.

**Parameters:**

- `location` (str): Location name (e.g., "Tokyo, Japan")
- `departure_date` (str, optional): Departure date in YYYY-MM-DD format
- `return_date` (str, optional): Return date in YYYY-MM-DD format

**Returns:** Weather forecast data including current conditions and 5-day forecast

### check_severe_weather

Check for severe weather conditions during travel period.

**Parameters:**

- `location` (str): Location name
- `departure_date` (str, optional): Departure date
- `return_date` (str, optional): Return date

**Returns:** List of weather risks with severity levels (thunderstorms, heavy rain, high winds, extreme temperatures)

### check_natural_disasters

Check for natural disaster alerts from GDACS.

**Parameters:**

- `location` (str): Location name
- `departure_date` (str, optional): Departure date
- `return_date` (str, optional): Return date

**Returns:** List of disaster alerts matching the destination

### web_search_risks

Search the web for travel risks using Tavily.

**Parameters:**

- `query` (str): Search query
- `destination` (str, optional): Destination name for context
- `max_results` (int, optional): Maximum number of results (default: 5)

**Returns:** Search results from Tavily

### comprehensive_risk_search

Perform comprehensive risk search across multiple categories.

**Parameters:**

- `destination` (str): Destination name
- `departure_date` (str, optional): Departure date
- `activities` (List[str], optional): List of planned activities
- `max_results_per_category` (int, optional): Max results per category (default: 3)

**Returns:** Organized results across general risks, weather risks, disaster risks, advisory risks, and activity-specific risks

### check_travel_advisories

Check for government travel advisories and warnings.

**Parameters:**

- `destination` (str): Destination name
- `country` (str, optional): Country name for broader search

**Returns:** List of travel advisories from government sources

## Additional Suggestions

Beyond the current tools, consider adding:

1. **Travel Advisory APIs** - Integrate government travel advisory feeds
2. **Health Alert Systems** - Check for disease outbreaks and health warnings
3. **Political Stability Checks** - Monitor political unrest and security alerts
4. **Crime Statistics** - Check crime rates and safety ratings for destinations
5. **Entry Requirements** - Check visa requirements and entry restrictions

## Troubleshooting

### Server Not Starting

1. Check that FastMCP is installed: `pip install fastmcp`
2. Verify the path in `mcp.json` is correct
3. Check that Python can find the `risk_agent` module
4. Review server logs for errors

### API Errors

1. Verify API keys are set correctly in `.env` or environment variables
2. Check API rate limits if getting errors
3. Ensure internet connectivity for API calls

### Tool Not Found

1. Restart Cursor after updating `mcp.json`
2. Verify the MCP server is running
3. Check that tools are properly decorated with `@mcp_server.tool()`

## Project Structure

```
risk_agent/
├── __init__.py          # Package initialization
├── mcp_server.py        # MCP server with tool definitions
├── config.py            # Configuration and API keys
└── README.md            # This file
```
