"""
API interface for the Classifier Agent
Provides a clean interface for integrating with the classifier
"""
from .classifier_agent import ClassifierAgent
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassifierAgentAPI:
    """API wrapper for Classifier Agent"""
    
    def __init__(self):
        self.agent = ClassifierAgent()
    
    def classify(self, query: str, detailed: bool = True) -> Dict[str, Any]:
        """
        Main API method for classifying queries
        
        Args:
            query: User query to classify
            detailed: Whether to return detailed results (default: True)
            
        Returns:
            Dictionary with classification results
        """
        try:
            result = self.agent.classify(query)
            
            if detailed:
                return result
            else:
                return {
                    'query': result['query'],
                    'classification': result['classification'],
                    'confidence': result['confidence']
                }
        
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            return {
                'success': False,
                'error': str(e),
                'classification': 'explanation',
                'confidence': 0.0
            }
    
    def get_classification_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get formatted classification details
        
        Args:
            result: Classification result dictionary
            
        Returns:
            Formatted details dictionary
        """
        classification = result.get('classification', 'unknown')
        
        type_descriptions = {
            'comparison': {
                'name': 'Comparison Query',
                'description': 'User wants to compare products or benefits',
                'next_steps': 'Retrieve benefit data for each product and create side-by-side comparison'
            },
            'explanation': {
                'name': 'Explanation Query',
                'description': 'User wants to understand or learn about coverage',
                'next_steps': 'Retrieve benefit details and policy text for explanation'
            },
            'eligibility': {
                'name': 'Eligibility Query',
                'description': 'User wants to know if they are covered',
                'next_steps': 'Check eligibility rules and conditions'
            },
            'scenario_analysis': {
                'name': 'Scenario Analysis Query',
                'description': 'User describes a hypothetical situation',
                'next_steps': 'Map scenario to benefits and walk through step-by-step'
            }
        }
        
        details = type_descriptions.get(classification, {
            'name': 'Unknown Query Type',
            'description': 'Query type could not be determined',
            'next_steps': 'Default to explanation workflow'
        })
        
        return {
            'query': result.get('query', ''),
            'classification': classification,
            'confidence': result.get('confidence', 0.0),
            'reasoning': result.get('reasoning', ''),
            'type_details': details,
            'entities': result.get('entities', {}),
            'metadata': result.get('metadata', {})
        }


# Convenience functions for easy integration
def classify_query(query: str) -> str:
    """
    Simple function to classify a query and return just the type
    
    Args:
        query: User query
        
    Returns:
        Classification type string
    """
    api = ClassifierAgentAPI()
    result = api.classify(query, detailed=False)
    return result.get('classification', 'explanation')


def classify_query_detailed(query: str) -> Dict[str, Any]:
    """
    Classify a query with detailed results
    
    Args:
        query: User query
        
    Returns:
        Detailed classification results dictionary
    """
    api = ClassifierAgentAPI()
    return api.get_classification_details(api.classify(query, detailed=True))


def classify_batch(queries: list) -> list:
    """
    Classify multiple queries in batch
    
    Args:
        queries: List of user queries
        
    Returns:
        List of classification results
    """
    api = ClassifierAgentAPI()
    results = []
    
    for query in queries:
        try:
            result = api.classify(query, detailed=False)
            results.append(result)
        except Exception as e:
            logger.error(f"Error classifying query '{query}': {e}")
            results.append({
                'query': query,
                'classification': 'explanation',
                'confidence': 0.0,
                'error': str(e)
            })
    
    return results

