"""
Decision Agent - Analyzes page sync data to determine if travel insurance is needed
Acts as a decision maker, not a summary generator
"""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS,
    CONFIDENCE_THRESHOLD, TRAVEL_KEYWORDS, INSURANCE_KEYWORDS,
    MASTER_AGENT_URL
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionAgent:
    """
    Decision Agent that analyzes page content to determine if:
    1. The page is travel-related
    2. Insurance might be needed for the travel activity
    3. Whether to prompt the user about insurance purchase
    
    This agent acts as a decision maker, not a content summarizer.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Decision Agent
        
        Args:
            model_name: OpenAI model name (default: from config)
        """
        self.model_name = model_name or OPENAI_MODEL
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=self.model_name,
            temperature=TEMPERATURE
        )
    
    def _is_stripe_payment_page(self, url: str, title: str, html_content: str) -> bool:
        """
        Check if the current page is a Stripe payment/checkout page
        
        Args:
            url: Page URL
            title: Page title
            html_content: Page HTML content
            
        Returns:
            True if this is a Stripe payment page
        """
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = html_content.lower()[:1000]  # Check first 1000 chars for speed
        
        # Stripe URL patterns
        stripe_domains = [
            'checkout.stripe.com',
            'js.stripe.com',
            'pay.stripe.com',
            'stripe.com/checkout',
            'stripe.com/pay',
            'stripe.com/c/pay',
        ]
        
        # Check URL for Stripe domains
        is_stripe_url = any(domain in url_lower for domain in stripe_domains)
        
        # Check for Stripe-specific content
        stripe_indicators = [
            'stripe',
            'checkout.stripe.com',
            'payment_intent',
            'payment_method',
            'stripe checkout',
            'pay with card',
        ]
        
        combined_text = f"{url_lower} {title_lower} {content_lower}"
        has_stripe_content = any(indicator in combined_text for indicator in stripe_indicators)
        
        return is_stripe_url or has_stripe_content
    
    def _quick_filter(self, page_content: str, url: str, title: str) -> bool:
        """
        Quick keyword-based filter to determine if page might be travel-related
        
        Args:
            page_content: Page text content
            url: Page URL
            title: Page title
            
        Returns:
            True if page contains travel-related keywords
        """
        combined_text = f"{url} {title} {page_content}".lower()
        
        # Check for travel keywords
        has_travel_keywords = any(keyword in combined_text for keyword in TRAVEL_KEYWORDS)
        
        return has_travel_keywords
    
    def analyze_page(self, url: str, title: str, html_content: str) -> Dict[str, Any]:
        """
        Analyze page content to determine if travel insurance might be needed
        
        Always sends HTML content to LLM for analysis, regardless of quick filter results.
        
        Args:
            url: Page URL
            title: Page title
            html_content: Page HTML/text content (may be truncated)
            
        Returns:
            Dictionary with decision and reasoning
        """
        logger.info(f"Analyzing page with LLM: {title} ({url})")
        
        # Early exit: Skip analysis if user is on Stripe payment page
        # They're already purchasing insurance, no need to prompt again
        if self._is_stripe_payment_page(url, title, html_content):
            logger.info(f"Skipping insurance prompt - user is on Stripe payment page: {url}")
            return {
                'should_prompt': False,
                'confidence': 1.0,
                'reasoning': 'User is on Stripe payment/checkout page - already purchasing insurance',
                'is_travel_related': False,
                'insurance_needed': False,
                'travel_context': '',
                'url': url,
                'title': title,
                'skipped_reason': 'stripe_payment_page'
            }
        
        # Always use LLM for analysis - send HTML content to LLM for decision making
        # Truncate HTML to reasonable size for API (increase limit since we're always using LLM)
        html_truncated = html_content[:10000]  # Increased to 10k chars for better analysis
        if len(html_content) > 10000:
            logger.info(f"HTML content truncated from {len(html_content)} to 10000 characters")
        
        decision_prompt = f"""You are a decision-making agent that analyzes web pages to determine if a user viewing a travel-related page might benefit from travel insurance.

Your task is to make a DECISION, not generate summaries. Analyze the page HTML content and decide:
1. Is this page travel-related? (flights, hotels, travel bookings, destinations, travel activities, etc.)
2. Does this travel activity/booking potentially need insurance coverage? (international travel, adventure activities, expensive trips, cancellable bookings, etc.)

IMPORTANT: If this is a payment page, checkout page, or the user is already purchasing insurance, set should_prompt to false. Do not prompt users who are already in the process of making a purchase.

Page Information:
URL: {url}
Title: {title}

Page HTML Content:
{html_truncated}
{f'\n[... content truncated, original length: {len(html_content)} characters ...]' if len(html_content) > 10000 else ''}

Based on this analysis, determine:
- Is this travel-related? (yes/no)
- Could this travel activity benefit from insurance? (yes/no)
- Should the user be prompted about insurance purchase? (yes/no - MUST be false if user is already on payment/checkout page)

Respond in this EXACT JSON format:
{{
    "is_travel_related": true/false,
    "insurance_needed": true/false,
    "should_prompt": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of your decision",
    "travel_context": "Brief description of travel type (e.g., 'international flight', 'hotel booking', 'adventure tour')"
}}

Only respond with the JSON object, no additional text."""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a precise decision-making agent. Make clear yes/no decisions about whether travel insurance should be offered to users based on page content."),
                HumanMessage(content=decision_prompt)
            ])
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Try to extract JSON from response (handle markdown code blocks)
            if response_text.startswith('```'):
                # Remove markdown code block markers
                lines = response_text.split('\n')
                response_text = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            # Parse JSON
            import json
            try:
                decision = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response if wrapped in text
                import re
                json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    decision = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from response")
            
            # Validate decision structure
            should_prompt = decision.get('should_prompt', False)
            confidence = float(decision.get('confidence', 0.0))
            is_travel_related = decision.get('is_travel_related', False)
            insurance_needed = decision.get('insurance_needed', False)
            
            # Apply confidence threshold
            if confidence < CONFIDENCE_THRESHOLD:
                should_prompt = False
                decision['reasoning'] = f"Confidence ({confidence:.2f}) below threshold ({CONFIDENCE_THRESHOLD})"
            
            logger.info(f"Decision: should_prompt={should_prompt}, confidence={confidence:.2f}, travel={is_travel_related}")
            
            return {
                'should_prompt': should_prompt,
                'confidence': confidence,
                'reasoning': decision.get('reasoning', 'Analysis completed'),
                'is_travel_related': is_travel_related,
                'insurance_needed': insurance_needed,
                'travel_context': decision.get('travel_context', ''),
                'url': url,
                'title': title
            }
        
        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            return {
                'should_prompt': False,
                'confidence': 0.0,
                'reasoning': f'Error during analysis: {str(e)}',
                'is_travel_related': False,
                'insurance_needed': False,
                'error': str(e)
            }
    
    def generate_insurance_prompt(self, decision_result: Dict[str, Any]) -> str:
        """
        Generate a prompt message to send to master agent for insurance purchase
        
        Args:
            decision_result: Result from analyze_page()
            
        Returns:
            Formatted prompt message for master agent
        """
        travel_context = decision_result.get('travel_context', 'travel plans')
        url = decision_result.get('url', '')
        title = decision_result.get('title', '')
        
        prompt = f"""Based on the user's current browsing activity, they appear to be planning or booking a trip.

Travel Context: {travel_context}
Page: {title}
URL: {url}

The user is viewing a travel-related page and may benefit from travel insurance coverage. 
Please provide a SHORT, CONCISE prompt (maximum 2 sentences, under 100 words) suggesting travel insurance.

Keep it brief and friendly. Focus on the value of coverage for their trip type."""
        
        return prompt

