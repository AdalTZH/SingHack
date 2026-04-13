"""
Summary Agent - Extracts key information from travel-related page content
Provides concise summaries for Master Agent context
"""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryAgent:
    """
    Summary Agent that extracts key information from travel-related pages
    
    This agent:
    1. Receives page content from Decision Agent
    2. Extracts important details (booking info, flight details, destinations, etc.)
    3. Creates concise summaries for Master Agent context
    4. Focuses on information relevant to insurance recommendations
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Summary Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=self.model_name,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        logger.info(f"Summary Agent initialized with model: {self.model_name}")
    
    def summarize_page(self, inner_text: str, url: str, title: str, travel_context: str = "") -> Dict[str, Any]:
        """
        Summarize travel-related page content
        
        Args:
            inner_text: Page text content (innerText from browser)
            url: Page URL
            title: Page title
            travel_context: Travel context from Decision Agent (e.g., "international flight")
            
        Returns:
            Dictionary with summary and metadata
        """
        logger.info(f"Summarizing page: {title} ({url})")
        
        # Build the summary prompt
        summary_prompt = f"""You are a travel information extraction agent. Analyze the following page content and extract KEY INFORMATION that would be relevant for providing travel insurance recommendations.

Page Information:
URL: {url}
Title: {title}
Travel Context: {travel_context}

Page Content:
{inner_text}

Extract and summarize the following information (if present):
1. **Travel Type**: What kind of travel is this? (flight, hotel, tour, activity, etc.)
2. **Destination**: Where is the user traveling to? (countries, cities)
3. **Dates**: Travel dates, booking dates, or time periods mentioned
4. **Booking Details**: Flight numbers, hotel names, tour operators, prices, confirmation numbers
5. **Activities**: Specific activities planned (adventure sports, excursions, etc.)
6. **Important Details**: Any other relevant information (travelers' names, group size, special requirements, cancellation policies, etc.)

CRITICAL REQUIREMENTS:
- Be CONCISE but COMPLETE - capture all important details
- Use bullet points or short sentences
- Focus on facts and specifics (numbers, dates, names, prices)
- Skip generic marketing content
- If booking/flight details are present, capture ALL of them
- Maximum 200 words

Respond in this format:
**Travel Type**: [type]
**Destination**: [location(s)]
**Dates**: [dates if available]
**Key Details**: [bullet points of important information]

If no specific details are found, provide a brief 1-2 sentence summary of what the page is about."""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a precise information extraction agent. Extract key travel details concisely but completely."),
                HumanMessage(content=summary_prompt)
            ])
            
            summary_text = response.content.strip()
            
            logger.info(f"Generated summary ({len(summary_text)} characters)")
            
            return {
                'success': True,
                'summary': summary_text,
                'url': url,
                'title': title,
                'travel_context': travel_context,
                'metadata': {
                    'model': self.model_name,
                    'summary_length': len(summary_text),
                    'content_length': len(inner_text)
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': f"Failed to summarize page: {title}",
                'url': url,
                'title': title,
                'travel_context': travel_context
            }


