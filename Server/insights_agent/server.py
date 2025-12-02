"""
Flask server for Insights Agent
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from .api import InsightsAgentAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the Insights Agent API
insights_api = InsightsAgentAPI()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Insights Agent',
        'version': '1.0.0'
    })


@app.route('/process', methods=['POST'])
def process_query():
    """
    Process a user query and determine if analytics should be performed
    
    Request body:
    {
        "query": "What are the risks of traveling to China?"
    }
    
    Response:
    {
        "should_analyze": true,
        "performed_analytics": true,
        "insights": "Persuasive insights text...",
        "reasoning": "Why analytics was performed",
        "confidence": 0.95,
        "query_results": [...],
        "execution_time": "2.5s"
    }
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({
                'error': 'No query provided',
                'should_analyze': False
            }), 400
        
        logger.info(f"Processing query: {user_query[:100]}...")
        
        result = insights_api.process_query(user_query)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'error': str(e),
            'should_analyze': False,
            'performed_analytics': False
        }), 500


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8008))
    
    print("="*70)
    print("INSIGHTS AGENT SERVER")
    print("="*70)
    print(f"Port: {port}")
    print("\nEndpoints:")
    print("  GET  /health     - Health check")
    print("  POST /process    - Process query and determine if analytics needed")
    print("\nStarting server on http://localhost:" + str(port))
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)

