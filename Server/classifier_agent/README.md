# Classifier Agent

An intelligent agent that classifies user insurance queries into one of four types using LangGraph and OpenAI's GPT models.

## Overview

The Classifier Agent is part of the SingHack Travel Insurance system. It uses AI to analyze user queries and route them to appropriate processing workflows:

1. **Comparison** - Compare products or benefits to find differences
2. **Explanation** - Understand or learn about coverage details
3. **Eligibility** - Check if user is covered or eligible
4. **Scenario Analysis** - Analyze hypothetical situations

## Architecture

### Key Components

- **ClassifierAgent** - Main agent using LangGraph for workflow orchestration
- **TaxonomyLoader** - Loads and queries insurance taxonomy JSON data
- **ClassifierAgentAPI** - Clean API interface for integration
- **MCP Server** - Exposes tools via Model Context Protocol

### Classification Workflow

```
User Query → Extract Entities → Classify → Validate → Return Result
```

The workflow uses a LangGraph StateGraph with these nodes:

1. **Extract Entities** - Identifies products, benefits, and keywords in the query
2. **Classify** - Uses LLM to classify query type with confidence score
3. **Validate** - Validates classification and adds metadata

## Installation

### Dependencies

The agent requires:
- Python 3.8+
- OpenAI API key
- LangGraph library
- LangChain libraries

Install dependencies:
```bash
pip install langgraph langchain-openai python-dotenv
```

### Configuration

Set up environment variables in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini
```

Ensure `Taxonomy_Hackathon.json` is in the Server directory.

## Usage

### Basic Usage

```python
from classifier_agent import classify_query

# Simple classification
query = "Which plan has better medical coverage?"
classification = classify_query(query)
print(f"Classified as: {classification}")
```

### Detailed Classification

```python
from classifier_agent import classify_query_detailed

query = "What is covered under home contents insurance?"
result = classify_query_detailed(query)

print(f"Type: {result['type_details']['name']}")
print(f"Description: {result['type_details']['description']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Next Steps: {result['type_details']['next_steps']}")
```

### Batch Classification

```python
from classifier_agent import classify_batch

queries = [
    "Compare Product A and Product B",
    "What does medical insurance cover?",
    "Am I covered for skiing?",
    "What happens if I break my leg abroad?"
]

results = classify_batch(queries)
for result in results:
    print(f"{result['query']}: {result['classification']}")
```

### Using the Agent Directly

```python
from classifier_agent import ClassifierAgent

agent = ClassifierAgent()

result = agent.classify("Which plan has better coverage?")
print(result)
# {
#     'query': 'Which plan has better coverage?',
#     'classification': 'comparison',
#     'confidence': 0.95,
#     'reasoning': '...',
#     'entities': {...},
#     'metadata': {...}
# }
```

### Using Taxonomy Loader

```python
from classifier_agent.taxonomy_loader import get_taxonomy_loader

loader = get_taxonomy_loader()

# Get benefit information
benefit = loader.get_benefit_by_name('home_contents')
print(benefit)

# Search benefits
results = loader.search_benefits('medical')
print(results)

# Get all benefit names
benefits = loader.get_benefit_names()
print(f"Total benefits: {len(benefits)}")
```

## MCP Integration

### Configure MCP Server in Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ClassifierAgentServer": {
      "command": "python",
      "args": ["-m", "classifier_agent.mcp_server"],
      "cwd": "C:\\Users\\YourPath\\SingHack-Backend\\Server"
    }
  }
}
```

### MCP Tools

The server provides 3 tools:

1. **classify_insurance_query** - Classify a single query
   - Parameters: `query` (str), `include_reasoning` (bool, optional)
   - Returns: Classification type, confidence, reasoning, next steps

2. **get_classification_details** - Get detailed information
   - Parameters: `classification_result` (dict)
   - Returns: Type details, next steps, entity extraction

3. **classify_batch_queries** - Classify multiple queries
   - Parameters: `queries` (list[str])
   - Returns: Individual results + summary statistics

### Using via Cursor AI

Once configured, you can ask Cursor:

- "Classify this query: Which plan has better coverage?"
- "What type of query is: Am I covered for pre-existing conditions?"

## Classification Examples

### Comparison Queries

```
✅ "Which plan has better medical coverage?"
✅ "Compare Product A and Product B"
✅ "What's the difference between travel insurance plans?"
```

**Output**: Routes to comparison agent for side-by-side analysis

### Explanation Queries

```
✅ "What is covered under home contents?"
✅ "Explain how medical evacuation works"
✅ "What does trip cancellation mean?"
```

**Output**: Routes to explanation agent with policy references

### Eligibility Queries

```
✅ "Am I covered for pre-existing conditions?"
✅ "Can I claim for skiing injuries?"
✅ "Am I eligible for dental coverage at age 70?"
```

**Output**: Routes to eligibility agent for yes/no with conditions

### Scenario Analysis Queries

```
✅ "What happens if I break my leg skiing in Japan?"
✅ "What if my flight is delayed for 24 hours?"
✅ "In case of a natural disaster, am I covered?"
```

**Output**: Routes to scenario agent for step-by-step analysis

## Architecture Details

### State Schema

```python
class ClassificationState(TypedDict):
    query: str                      # User query
    classification: str             # Classified type
    confidence: float              # Confidence score (0-1)
    reasoning: str                 # Reasoning for classification
    extracted_entities: Dict       # Products, benefits, keywords
    metadata: Dict                 # Additional metadata
```

### Entity Extraction

The agent extracts:
- **Products**: Product A, Product B, Product C, or real names
- **Benefits**: Benefit names from taxonomy
- **Keywords**: Classification keywords from query

### Classification Method

Uses OpenAI GPT with:
- Temperature: 0.1 (deterministic)
- Structured JSON output
- Keyword-based fallback
- Confidence scoring

## Configuration

### Classification Types

Defined in `config.py`:
```python
CLASSIFICATION_TYPES = [
    'comparison',
    'explanation',
    'eligibility',
    'scenario_analysis'
]
```

### Product Mappings

```python
PRODUCT_NAMES = {
    'Product A': 'Scootsurance Travel Insurance',
    'Product B': 'COVID-19 COVER (TravelEasy)',
    'Product C': 'TravelEasy / TravelEasy Pre-Ex'
}
```

### Confidence Threshold

```python
CONFIDENCE_THRESHOLD = 0.7  # High confidence threshold
```

## Testing

Run examples:
```bash
python -m classifier_agent.example_usage
```

Test individual components:
```python
from classifier_agent import ClassifierAgent

agent = ClassifierAgent()
result = agent.classify("Test query")
print(result)
```

## Integration with Other Agents

The Classifier Agent is designed to work with specialized agents:

```
Classifier Agent → Routes to:
    ├─ Comparison Agent (for comparison queries)
    ├─ Explanation Agent (for explanation queries)
    ├─ Eligibility Agent (for eligibility queries)
    └─ Scenario Agent (for scenario analysis)
```

Each downstream agent receives:
- Classification type
- Extracted entities
- Original query
- Suggested workflow

## Error Handling

- **Invalid classification**: Falls back to 'explanation' type
- **Low confidence**: Returns confidence < threshold with warning
- **Taxonomy loading errors**: Logs error, continues with limited functionality
- **LLM errors**: Falls back to keyword-based classification

## Performance

- **Single query**: ~1-2 seconds (LLM call)
- **Batch 10 queries**: ~10-15 seconds (sequential)
- **Cache-friendly**: Can be optimized with caching

## Future Enhancements

- [ ] Add caching for repeated queries
- [ ] Implement parallel batch processing
- [ ] Add confidence threshold tuning
- [ ] Support multi-language queries
- [ ] Add query history tracking
- [ ] Implement feedback loop for classification accuracy

## License

Part of SingHack Travel Insurance System

