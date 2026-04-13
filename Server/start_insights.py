"""
Flask API Server for Natural Language to Neo4j Cypher Queries
Uses GPT to convert text queries to Cypher, execute them, and analyze results
"""

from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from neo4j.time import Date, DateTime
from openai import OpenAI
import os
from typing import Dict, List, Any
import json
from datetime import date, datetime

app = Flask(__name__)

# Configuration
NEO4J_CONFIG = {
    'uri': 'neo4j+s://68783b43.databases.neo4j.io',  # Change if needed
    'user': 'neo4j',                 # Change to your username
    'password': 'GEAVC0YDgq022XAXy7098osogQpPxfXmaFZJ4QKxrTc'           # Change to your password
}

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
openai_client = OpenAI(api_key=OPENAI_API_KEY)


class Neo4jQueryEngine:
    """Handle Neo4j connections and query execution"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.cached_schema = None
    
    def close(self):
        self.driver.close()
    
    def _serialize_neo4j_types(self, obj):
        """Convert Neo4j types to JSON-serializable types"""
        if isinstance(obj, (Date, date)):
            return obj.isoformat()
        elif isinstance(obj, (DateTime, datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_neo4j_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_neo4j_types(item) for item in obj]
        else:
            return obj
    
    def execute_query(self, cypher_query: str) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        with self.driver.session() as session:
            result = session.run(cypher_query)
            records = [dict(record) for record in result]
            # Serialize Neo4j date/time objects
            return [self._serialize_neo4j_types(record) for record in records]
    
    def extract_actual_values(self) -> Dict[str, Any]:
        """Extract actual values from the database for each category"""
        if self.cached_schema:
            return self.cached_schema
            
        print("  Extracting actual values from Neo4j...")
        schema_data = {}
        
        with self.driver.session() as session:
            # Get all destinations
            result = session.run("""
                MATCH (d:Destination)
                RETURN d.name as name
                ORDER BY name
            """)
            schema_data['destinations'] = [record['name'] for record in result]
            
            # Get all claim types
            result = session.run("""
                MATCH (ct:ClaimType)
                RETURN ct.name as name
                ORDER BY name
            """)
            schema_data['claim_types'] = [record['name'] for record in result]
            
            # Get all causes of loss
            result = session.run("""
                MATCH (c:CauseOfLoss)
                RETURN c.name as name
                ORDER BY name
            """)
            schema_data['causes_of_loss'] = [record['name'] for record in result]
            
            # Get all loss types
            result = session.run("""
                MATCH (lt:LossType)
                RETURN lt.name as name
                ORDER BY name
            """)
            schema_data['loss_types'] = [record['name'] for record in result]
            
            # Get claim statistics
            result = session.run("""
                MATCH (c:Claim)
                RETURN 
                    count(c) as total_claims,
                    min(c.gross_paid) as min_paid,
                    max(c.gross_paid) as max_paid,
                    avg(c.gross_paid) as avg_paid
            """)
            stats = result.single()
            schema_data['statistics'] = {
                'total_claims': stats['total_claims'],
                'min_paid': float(stats['min_paid']) if stats['min_paid'] else 0,
                'max_paid': float(stats['max_paid']) if stats['max_paid'] else 0,
                'avg_paid': float(stats['avg_paid']) if stats['avg_paid'] else 0
            }
        
        self.cached_schema = schema_data
        print(f"  ✓ Found {len(schema_data['destinations'])} destinations, "
              f"{len(schema_data['claim_types'])} claim types, "
              f"{len(schema_data['causes_of_loss'])} causes")
        
        return schema_data


class GPTCypherGenerator:
    """Generate Cypher queries from natural language using GPT"""
    
    def __init__(self, neo4j_engine):
        self.neo4j = neo4j_engine
        self.schema = """
        Neo4j Graph Schema:
        
        Nodes:
        - Claim: {
            id (string),
            accident_date (date),
            gross_paid (float) - THE CLAIM PAYOUT AMOUNT IN DOLLARS
          }
        - Destination: {name (string)} - Country where claim occurred
        - ClaimType: {name (string)} - Type of claim (Medical, Baggage, etc.)
        - CauseOfLoss: {name (string)} - What caused the claim (Illness, Loss, etc.)
        - LossType: {name (string)} - Category of loss
        
        Relationships:
        - (Claim)-[:OCCURRED_IN]->(Destination)
        - (Claim)-[:IS_TYPE]->(ClaimType)
        - (Claim)-[:CAUSED_BY]->(CauseOfLoss)
        - (Claim)-[:HAS_LOSS_TYPE]->(LossType)
    
        
        IMPORTANT: Use c.gross_paid to calculate averages, sums, min, max of claim amounts!
        
        Example Queries Using gross_paid:
        - Average: avg(c.gross_paid)
        - Total: sum(c.gross_paid)
        - Highest: max(c.gross_paid)
        - Count high-value: WHERE c.gross_paid > 500
        """
    
    def generate_cypher_queries(self, user_query: str) -> List[Dict[str, str]]:
        """Generate 3 Cypher queries based on user's natural language query"""

        actual_values = self.neo4j.extract_actual_values()
        
        prompt = f"""You are a Neo4j Cypher query expert. Given a user's natural language question about travel insurance claims, generate 3 DIFFERENT Cypher queries that extract meaningful insights.

Base Schema:
{self.schema}


Destinations: {actual_values['destinations']}
Claim Types: {actual_values['claim_types']}
Causes of Loss: {actual_values['causes_of_loss']}
Loss Types: {actual_values['loss_types']}
 
Use ONLY these values in filters, comparisons, and WHERE clauses.

User Question: "{user_query}"

Generate 3 different Cypher queries that would help answer this question from different angles:
1. A query focusing on aggregated statistics (averages, counts, sums)
2. A query focusing on patterns and relationships
3. A query focusing on trends or comparisons

Return ONLY a JSON array with this structure:
[
  {{
    "title": "Brief title of what this query finds",
    "cypher": "MATCH ... RETURN ...",
    "explanation": "What this query reveals"
  }},
  ...
]

Important:
- Make queries realistic and executable
- Use proper Cypher syntax
- Include LIMIT clauses where appropriate
- Return meaningful aggregations or insights
- NO markdown formatting, just pure JSON
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a Neo4j Cypher expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        return json.loads(content)
    
    def analyze_results(self, user_query: str, query_results: List[Dict]) -> str:
        """Analyze query results and provide meaningful insights"""
        
        prompt = f"""You are a persuasive insurance advisor analyzing travel insurance claims data.

User asked: "{user_query}"

Query results:
{json.dumps(query_results, indent=2, default=str)}

Provide a SHORT, PERSUASIVE summary (3-4 sentences max) that:
1. Highlights key risks or statistics from the data
2. Creates urgency or awareness about potential costs
3. Naturally leads to why insurance is important
4. Uses specific numbers to make it compelling

Write in a conversational, slightly urgent tone that would persuade potential clients to purchase travel insurance. Focus on the "what could go wrong" angle with real data backing it up.

Keep it brief and punchy - this is for potential clients, not detailed analysis.
"""

        response = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "You are a persuasive insurance sales advisor. Keep responses brief and compelling."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content


# Initialize engines
neo4j_engine = Neo4jQueryEngine(
    uri=NEO4J_CONFIG['uri'],
    user=NEO4J_CONFIG['user'],
    password=NEO4J_CONFIG['password']
)

gpt_engine = GPTCypherGenerator(neo4j_engine)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Text-to-Cypher API',
        'neo4j_connected': True
    })


@app.route('/query', methods=['POST'])
def process_query():
    """
    Main endpoint: Process natural language query
    
    Request body:
    {
        "query": "What is the average claim amount for medical expenses in China?"
    }
    
    Response:
    {
        "user_query": "...",
        "cypher_queries": [...],
        "query_results": [...],
        "analysis": "...",
        "execution_time": "..."
    }
    """
    try:
        import time
        start_time = time.time()
        
        # Get user query
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({'error': 'No query provided'}), 400
        
        print(f"\n{'='*70}")
        print(f"Processing query: {user_query}")
        print(f"{'='*70}")
        
        # Step 1: Generate Cypher queries using GPT
        print("\n[1/3] Generating Cypher queries...")
        cypher_queries = gpt_engine.generate_cypher_queries(user_query)
        print(f"✓ Generated {len(cypher_queries)} queries")
        
        # Step 2: Execute queries against Neo4j
        print("\n[2/3] Executing queries against Neo4j...")
        query_results = []
        for i, query_info in enumerate(cypher_queries, 1):
            print(f"  Executing query {i}: {query_info['title']}")
            try:
                results = neo4j_engine.execute_query(query_info['cypher'])
                query_results.append({
                    'title': query_info['title'],
                    'explanation': query_info['explanation'],
                    'cypher': query_info['cypher'],
                    'results': results,
                    'result_count': len(results)
                })
                print(f"  ✓ Retrieved {len(results)} results")
            except Exception as e:
                print(f"  ✗ Query failed: {e}")
                query_results.append({
                    'title': query_info['title'],
                    'explanation': query_info['explanation'],
                    'cypher': query_info['cypher'],
                    'error': str(e),
                    'results': []
                })
        
        # Step 3: Analyze results using GPT
        print("\n[3/3] Analyzing results with GPT...")
        analysis = gpt_engine.analyze_results(user_query, query_results)
        print("✓ Analysis complete")
        
        execution_time = time.time() - start_time
        
        # Prepare response
        response = {
            'user_query': user_query,
            'cypher_queries': cypher_queries,
            'query_results': query_results,
            'analysis': analysis,
            'execution_time': f"{execution_time:.2f}s"
        }
        
        print(f"\n{'='*70}")
        print("ANALYSIS:")
        print(f"{'='*70}")
        print(analysis)
        print(f"{'='*70}\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/schema', methods=['GET'])
def get_schema():
    """Get the Neo4j graph schema with actual values"""
    try:
        schema_info = {
            'base_schema': gpt_engine.base_schema,
            'actual_values': neo4j_engine.extract_actual_values(),
            'full_schema': gpt_engine.get_full_schema()
        }
        return jsonify(schema_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test-queries', methods=['GET'])
def test_queries():
    """Get example test queries"""
    examples = [
        "What is the average claim amount for medical expenses in China?",
        "Which destinations have the highest claim costs?",
        "Show me patterns between causes of loss and claim types",
        "What are the trends in baggage loss claims?",
        "Compare medical expenses across different countries",
        "Which causes of loss result in the highest payouts?",
        "Show me claims data for Thailand",
        "What's the distribution of claim types?",
        "Find expensive claims over $1000",
        "Analyze claims by destination and cause"
    ]
    return jsonify({
        'example_queries': examples,
        'usage': 'POST to /query with {"query": "your question here"}'
    })


if __name__ == '__main__':
    print("="*70)
    print("TEXT-TO-CYPHER API SERVER")
    print("="*70)
    print(f"Neo4j URI: {NEO4J_CONFIG['uri']}")
    print(f"OpenAI Model: gpt-4o, gpt-5.1")
    print("\nEndpoints:")
    print("  GET  /health        - Health check")
    print("  GET  /schema        - View graph schema")
    print("  GET  /test-queries  - Example queries")
    print("  POST /query         - Process natural language query")
    print("\nStarting server on http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)