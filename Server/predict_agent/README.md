# Predict Agent MCP Server

An MCP (Model Context Protocol) server that exposes tools for insurance plan recommendations based on historical claims data analysis.

## Overview

The Predict Agent analyzes historical claims data from a PostgreSQL database to recommend the most suitable insurance plans for users based on their travel profile, destination, coverage priorities, and risk factors.

## Tools Provided

### 1. `find_insurance_plans`
Find suitable insurance plans based on comprehensive user data.

**Parameters:**
- `age` (required): User's age
- `travel_destination` (required): Travel destination (e.g., "Japan", "Thailand")
- `trip_duration_days` (required): Trip duration in days
- `trip_type` (optional): Type of trip (e.g., "business", "leisure", "adventure")
- `travel_style` (optional): Travel style (e.g., "budget", "luxury", "backpacking")
- `has_pre_existing_conditions` (optional): Whether user has pre-existing medical conditions
- `plans_adventure_activities` (optional): Whether user plans adventure activities
- `traveling_with_children` (optional): Whether traveling with children
- `traveling_with_valuables` (optional): Whether traveling with valuable items
- `priority_medical_coverage` (optional): Medical coverage priority (default: True)
- `priority_trip_cancellation` (optional): Trip cancellation priority (default: False)
- `priority_baggage_coverage` (optional): Baggage coverage priority (default: False)
- `priority_liability_coverage` (optional): Liability coverage priority (default: False)
- `budget_range` (optional): Budget range (e.g., "low", "medium", "high")
- `frequent_traveler` (optional): Whether user is a frequent traveler
- `previous_claims` (optional): Number of previous claims (default: 0)
- `top_n` (optional): Number of top recommendations (default: 3)

**Returns:** Dictionary with recommendations including:
- Ranked list of recommended products
- Composite scores
- Reasoning for each recommendation
- Product statistics and performance metrics
- Match scores for different factors

### 2. `get_product_statistics`
Get performance statistics for insurance products.

**Parameters:**
- `product_name` (optional): Filter by product name (partial match)
- `limit` (optional): Maximum number of results (default: 10)

**Returns:** Dictionary with:
- List of products with statistics
- Total claims per product
- Average claim amounts
- Processing times
- Coverage diversity metrics

### 3. `analyze_destination_coverage`
Analyze insurance product coverage for a specific destination.

**Parameters:**
- `destination` (required): Travel destination to analyze

**Returns:** Dictionary with:
- Products that have handled claims for the destination
- Total claims per product
- Claim types covered
- Product performance metrics for that destination

## Setup

### 1. Install Dependencies

```bash
pip install fastmcp psycopg2-binary pandas numpy python-dotenv
```

### 2. Configure Database

Set database credentials in `.env` file:

```env
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Or use the default configuration in `config.py` (already configured for hackathon database).

### 3. Configure MCP Server in Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "PredictAgentServer": {
      "command": "python",
      "args": ["-m", "predict_agent.mcp_server"],
      "cwd": "C:\\Users\\Sean\\Documents\\CS Projects\\singhacks"
    }
  }
}
```

### 4. Restart Cursor

After updating `mcp.json`, restart Cursor to load the MCP server.

## Usage

### Example: Find Insurance Plans

```python
from predict_agent.mcp_server import _find_insurance_plans_impl

result = _find_insurance_plans_impl(
    age=35,
    travel_destination="Japan",
    trip_duration_days=10,
    priority_medical_coverage=True,
    top_n=3
)

print(result)
```

### Example: Get Product Statistics

```python
from predict_agent.mcp_server import _get_product_statistics_impl

stats = _get_product_statistics_impl(limit=5)
print(stats)
```

### Example: Analyze Destination Coverage

```python
from predict_agent.mcp_server import _analyze_destination_coverage_impl

coverage = _analyze_destination_coverage_impl("Japan")
print(coverage)
```

## How It Works

1. **Data Analysis**: The agent queries a PostgreSQL database containing historical claims data
2. **Scoring System**: Products are scored based on:
   - Destination match (30% weight)
   - Claim type match (25% weight)
   - Claim frequency (15% weight)
   - Claim severity (15% weight)
   - Processing efficiency (15% weight)
3. **User Adjustments**: Scores are adjusted based on user profile (age, activities, trip duration)
4. **Recommendations**: Top N products are returned with detailed reasoning

## Project Structure

```
predict_agent/
├── __init__.py           # Package initialization
├── mcp_server.py         # MCP server with tool definitions
├── config.py             # Configuration and database settings
├── predict_agent.py      # Main prediction logic
├── api.py                # API wrapper
├── user_data_model.py    # User data model
├── database.py           # Database connection and queries
├── example_usage.py      # Usage examples
└── README.md             # This file
```

## Testing

Run example usage:

```bash
python -m predict_agent.example_usage
```

Or test the MCP server manually:

```bash
python -m predict_agent.mcp_server
```

## Integration with Risk Agent

The Predict Agent can be used alongside the Risk Agent:

1. **Risk Agent** identifies travel risks (weather, disasters, etc.)
2. **Predict Agent** recommends insurance plans based on risks and user profile
3. Both agents can be called automatically by Cursor's AI assistant

## Troubleshooting

### Database Connection Errors

1. Verify database credentials in `.env` or `config.py`
2. Check database is accessible from your network
3. Test connection: `python -c "from predict_agent.database import DatabaseConnection; db = DatabaseConnection(); print(db.connect())"`

### No Recommendations Returned

1. Check if database has claims data
2. Verify destination matches exist in database
3. Try a more general destination name

### MCP Server Not Starting

1. Ensure FastMCP is installed: `pip install fastmcp`
2. Check Python path in `mcp.json` is correct
3. Verify module can be imported: `python -c "import predict_agent.mcp_server"`

