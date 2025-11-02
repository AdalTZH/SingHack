"""
Classifier Agent - Classifies insurance queries using LangGraph
"""
from typing import Dict, List, Optional, Any, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator
import logging
import json

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, CLASSIFICATION_TYPES,
    PRODUCT_NAMES, CLASSIFICATION_KEYWORDS, CONFIDENCE_THRESHOLD
)
from .taxonomy_loader import get_taxonomy_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the state for classification workflow
class ClassificationState(TypedDict):
    """State schema for the classification workflow"""
    query: str  # User query
    classification: str  # Classified query type
    confidence: float  # Confidence score
    reasoning: str  # Reasoning for classification
    extracted_entities: Dict[str, Any]  # Extracted entities (products, benefits, etc.)
    metadata: Dict[str, Any]  # Additional metadata


class ClassifierAgent:
    """
    Agent that classifies user queries into one of four types:
    - Comparison: Compare products/benefits
    - Explanation: Explain benefits/coverage
    - Eligibility: Check coverage eligibility
    - Scenario Analysis: Analyze hypothetical scenarios
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Classifier Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=self.model_name,
            temperature=0.1
        )
        self.taxonomy_loader = get_taxonomy_loader()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow for query classification
        
        Returns:
            Compiled StateGraph
        """
        # Create the graph builder
        graph_builder = StateGraph(ClassificationState)
        
        # Add nodes
        graph_builder.add_node("extract_entities", self._extract_entities)
        graph_builder.add_node("classify_query", self._classify_query)
        graph_builder.add_node("validate_classification", self._validate_classification)
        
        # Define edges
        graph_builder.add_edge(START, "extract_entities")
        graph_builder.add_edge("extract_entities", "classify_query")
        graph_builder.add_edge("classify_query", "validate_classification")
        graph_builder.add_edge("validate_classification", END)
        
        # Compile the graph
        return graph_builder.compile()
    
    def _extract_entities(self, state: ClassificationState) -> Dict[str, Any]:
        """
        Extract entities from the query (products, benefits, etc.)
        
        Args:
            state: Current state
            
        Returns:
            Updated state with extracted entities
        """
        query = state.get('query', '')
        logger.info(f"Extracting entities from query: {query}")
        
        # Use LLM to extract entities
        extraction_prompt = f"""Extract relevant entities from this insurance query.

Query: "{query}"

Extract the following information:
1. Product names mentioned (Product A, Product B, Product C, or their real names)
2. Benefit names or coverage types mentioned
3. Specific parameters or limits mentioned
4. Any conditions or scenarios described

Return your response in a clear format. If no specific entities are found, say "None found".

Available products:
{', '.join([f'{k}: {v}' for k, v in PRODUCT_NAMES.items()])}

List of available benefits: {', '.join(self.taxonomy_loader.get_benefit_names()[:20])}... (many more)"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert at extracting structured information from insurance queries."),
                HumanMessage(content=extraction_prompt)
            ])
            
            extracted_text = response.content
            
            # Store extracted information
            extracted_entities = {
                'raw_extraction': extracted_text,
                'products': self._extract_products(query, extracted_text),
                'benefits': self._extract_benefits(query, extracted_text),
                'keywords': self._extract_keywords(query)
            }
            
            logger.info(f"Extracted entities: {extracted_entities}")
            
            return {
                'extracted_entities': extracted_entities
            }
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                'extracted_entities': {
                    'raw_extraction': 'Error during extraction',
                    'products': [],
                    'benefits': [],
                    'keywords': []
                }
            }
    
    def _extract_products(self, query: str, extraction: str) -> List[str]:
        """Extract product names from query"""
        products_found = []
        
        # Check for product names
        query_lower = query.lower()
        extraction_lower = extraction.lower()
        
        for product_key, product_name in PRODUCT_NAMES.items():
            if product_key.lower() in query_lower or product_key.lower() in extraction_lower:
                products_found.append(product_key)
        
        return products_found
    
    def _extract_benefits(self, query: str, extraction: str) -> List[str]:
        """Extract benefit names from query"""
        benefits_found = []
        
        query_lower = query.lower()
        extraction_lower = extraction.lower()
        
        # Get all benefit names
        all_benefits = self.taxonomy_loader.get_benefit_names()
        
        for benefit in all_benefits:
            benefit_lower = benefit.lower()
            # Check if benefit is mentioned in query or extraction
            if benefit_lower in query_lower or benefit_lower in extraction_lower:
                benefits_found.append(benefit)
        
        return benefits_found[:10]  # Limit to 10
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query"""
        keywords_found = []
        query_lower = query.lower()
        
        # Check against classification keywords
        for category, keyword_list in CLASSIFICATION_KEYWORDS.items():
            for keyword in keyword_list:
                if keyword.lower() in query_lower:
                    keywords_found.append(keyword)
        
        return keywords_found
    
    def _classify_query(self, state: ClassificationState) -> Dict[str, Any]:
        """
        Classify the query into one of the four types
        
        Args:
            state: Current state
            
        Returns:
            Updated state with classification
        """
        query = state.get('query', '')
        extracted_entities = state.get('extracted_entities', {})
        
        logger.info(f"Classifying query: {query}")
        
        # Build classification prompt
        classification_prompt = f"""Classify this insurance query into ONE of these four types:

1. COMPARISON - User wants to compare products or benefits to find differences
   Examples: "Which plan has better coverage?", "Compare Product A and Product B"
   
2. EXPLANATION - User wants to understand or learn about a benefit or coverage
   Examples: "What is covered under home contents?", "Explain medical coverage"
   
3. ELIGIBILITY - User wants to know if they are covered or eligible for something
   Examples: "Am I covered for skiing?", "Can I claim for pre-existing conditions?"
   
4. SCENARIO ANALYSIS - User describes a hypothetical situation and wants to know what happens
   Examples: "What if I break my leg skiing?", "What happens if my flight is delayed?"

Query: "{query}"

Extracted entities: {extracted_entities}

Respond with ONLY a JSON object in this format:
{{
    "classification": "comparison | explanation | eligibility | scenario_analysis",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of why this classification"
}}"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert at classifying insurance queries. Always respond with valid JSON."),
                HumanMessage(content=classification_prompt)
            ])
            
            # Parse JSON response
            result = json.loads(response.content.strip())
            
            classification = result.get('classification', 'explanation')
            confidence = float(result.get('confidence', 0.5))
            reasoning = result.get('reasoning', 'No reasoning provided')
            
            logger.info(f"Classification: {classification} (confidence: {confidence})")
            
            return {
                'classification': classification,
                'confidence': confidence,
                'reasoning': reasoning
            }
        
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            # Fallback to keyword-based classification
            fallback = self._keyword_based_classification(query)
            return {
                'classification': fallback['type'],
                'confidence': fallback['confidence'],
                'reasoning': 'Fallback keyword-based classification'
            }
    
    def _keyword_based_classification(self, query: str) -> Dict[str, Any]:
        """Fallback keyword-based classification"""
        query_lower = query.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        for category, keyword_list in CLASSIFICATION_KEYWORDS.items():
            score = sum(1 for keyword in keyword_list if keyword in query_lower)
            category_scores[category] = score
        
        # Find category with highest score
        if max(category_scores.values()) == 0:
            # Default to explanation if no matches
            return {'type': 'explanation', 'confidence': 0.3}
        
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # Convert score to confidence (simple linear mapping)
        confidence = min(best_category[1] / 5.0, 0.9)
        
        return {'type': best_category[0], 'confidence': confidence}
    
    def _validate_classification(self, state: ClassificationState) -> Dict[str, Any]:
        """
        Validate the classification and add metadata
        
        Args:
            state: Current state
            
        Returns:
            Updated state with metadata
        """
        classification = state.get('classification', '')
        confidence = state.get('confidence', 0.0)
        
        # Validate classification is valid
        if classification not in CLASSIFICATION_TYPES:
            logger.warning(f"Invalid classification: {classification}, defaulting to explanation")
            classification = 'explanation'
        
        # Add metadata
        metadata = {
            'model_used': self.model_name,
            'is_high_confidence': confidence >= CONFIDENCE_THRESHOLD,
            'taxonomy_loaded': self.taxonomy_loader.taxonomy_data is not None
        }
        
        logger.info(f"Classification validated: {classification} (confidence: {confidence})")
        
        return {
            'metadata': metadata
        }
    
    def classify(self, query: str) -> Dict[str, Any]:
        """
        Main classification method
        
        Args:
            query: User query to classify
            
        Returns:
            Dictionary with classification results
        """
        logger.info(f"Classifying query: {query}")
        
        # Invoke the graph
        result = self.graph.invoke({
            'query': query,
            'classification': '',
            'confidence': 0.0,
            'reasoning': '',
            'extracted_entities': {},
            'metadata': {}
        })
        
        return {
            'query': result['query'],
            'classification': result['classification'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'entities': result['extracted_entities'],
            'metadata': result['metadata']
        }


# Convenience function
def classify_query_type(query: str) -> str:
    """
    Simple function to classify a query and return just the type
    
    Args:
        query: User query
        
    Returns:
        Classification type string
    """
    agent = ClassifierAgent()
    result = agent.classify(query)
    return result['classification']

