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
    CONFIDENCE_THRESHOLD, TRAVEL_KEYWORDS, INSURANCE_KEYWORDS
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
    
    def _is_stripe_payment_page(self, url: str, title: str, inner_text: str) -> bool:
        """
        Check if the current page is a Stripe payment/checkout page
        
        Args:
            url: Page URL
            title: Page title
            inner_text: Page text content
            
        Returns:
            True if this is a Stripe payment page
        """
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = inner_text.lower()[:1000]  # Check first 1000 chars for speed
        
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
    
    def analyze_page(self, url: str, title: str, inner_text: str) -> Dict[str, Any]:
        """
        Analyze page content to determine if travel insurance might be needed
        
        Always sends text content to LLM for analysis, regardless of quick filter results.
        
        Args:
            url: Page URL
            title: Page title
            inner_text: Page text content (innerText from browser, may be truncated)
            
        Returns:
            Dictionary with decision and reasoning
        """
        logger.info(f"Analyzing page with LLM: {title} ({url})")
        
        # Early exit: Skip analysis if user is on Stripe payment page
        # They're already purchasing insurance, no need to prompt again
        if self._is_stripe_payment_page(url, title, inner_text):
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
        
        # Always use LLM for analysis - send text content to LLM for decision making
        # Truncate text to reasonable size for API (increase limit since we're always using LLM)
        text_truncated = inner_text[:10000]  # Increased to 10k chars for better analysis
        if len(inner_text) > 10000:
            logger.info(f"Text content truncated from {len(inner_text)} to 10000 characters")
        
        decision_prompt = f"""You are a decision-making agent that analyzes web pages to determine if a user viewing a travel-related page might benefit from travel insurance.

Your task is to make a DECISION, not generate summaries. Analyze the page text content and decide:
1. Is this page travel-related? (flights, hotels, travel bookings, destinations, travel activities, etc.)
2. Does this travel activity/booking potentially need insurance coverage? (international travel, adventure activities, expensive trips, cancellable bookings, etc.)

Page Information:
URL: {url}
Title: {title}

Page Text Content:
{text_truncated}
{f'\n[... content truncated, original length: {len(inner_text)} characters ...]' if len(inner_text) > 10000 else ''}

Based on this analysis, determine:
- Is this travel-related? (yes/no)
- Could this travel activity benefit from insurance? (yes/no)
- Should the user be prompted about insurance purchase? (yes/no - should be true if travel-related)

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
            
            # Override: Always prompt if travel-related, regardless of payment/checkout status
            if is_travel_related:
                should_prompt = True
                if decision.get('reasoning'):
                    decision['reasoning'] = f"{decision.get('reasoning')} (Prompting enabled: page is travel-related)"
            
            # Apply confidence threshold (but don't override travel-related prompt)
            if confidence < CONFIDENCE_THRESHOLD and not is_travel_related:
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
    
    def generate_persuasion_message(self, decision_result: Dict[str, Any]) -> str:
        """
        Generate a compelling 1-liner persuasion message to display in cursor textbox
        
        Args:
            decision_result: Result from analyze_page()
            
        Returns:
            A single, persuasive line encouraging insurance purchase
        """
        travel_context = decision_result.get('travel_context', 'travel plans')
        url = decision_result.get('url', '')
        title = decision_result.get('title', '')
        is_travel_related = decision_result.get('is_travel_related', False)
        insurance_needed = decision_result.get('insurance_needed', False)
        
        # Extract key information from travel context
        persuasion_prompt = f"""You are a travel insurance advisor. Based on the user's browsing activity, create a SINGLE, catchy one-liner to persuade them to purchase travel insurance.

Travel Context: {travel_context}
Page: {title}
URL: {url}
Travel-related: {is_travel_related}
Insurance needed: {insurance_needed}

CRITICAL REQUIREMENTS:
- Must be exactly ONE line (no line breaks)
- Maximum 20 words (strict limit - count carefully)
- CATCHY and memorable - use action words
- Short and punchy - won't take up screen space
- Focus on the specific travel activity or destination
- Create urgency or highlight value
- Friendly and professional tone
- Make it snappy and attention-grabbing

Examples of good catchy persuasion lines (all under 20 words):
- "Protect your adventure! Travel insurance = peace of mind ✈️"
- "Don't let surprises ruin your trip - get covered now!"
- "Travel insurance: Your safety net for unexpected adventures"
- "Secure your journey with travel insurance - worry-free travel awaits!"

Generate ONLY the one-liner message, nothing else. No quotes, no explanations, just the message text. Remember: MAX 20 WORDS."""

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a persuasive travel insurance advisor. Generate compelling, concise one-liners to encourage insurance purchases."),
                HumanMessage(content=persuasion_prompt)
            ])
            
            # Extract the message
            message = response.content.strip()
            
            # Remove quotes if present
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            elif message.startswith("'") and message.endswith("'"):
                message = message[1:-1]
            
            # Remove any markdown formatting
            if message.startswith('```'):
                lines = message.split('\n')
                message = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            # Take only the first line and limit to 20 words
            message = message.split('\n')[0].strip()
            words = message.split()
            original_word_count = len(words)
            
            if original_word_count > 20:
                # Truncate to 20 words
                message = ' '.join(words[:20])
                # Remove trailing punctuation if it looks incomplete
                if message and message[-1] in [',', ';', ':']:
                    message = message[:-1].strip()
                logger.warning(f"Message exceeded 20 words ({original_word_count} words), truncated to 20 words")
            
            final_word_count = len(message.split())
            logger.info(f"Generated persuasion message ({final_word_count} words): {message}")
            return message
        
        except Exception as e:
            logger.error(f"Error generating persuasion message: {e}")
            # Fallback message (max 20 words, catchy)
            if travel_context:
                # Try to keep it short and catchy
                context_words = travel_context.split()[:3]  # Take first 3 words max
                context_short = ' '.join(context_words)
                return f"Protect your {context_short} with travel insurance! ✈️"
            else:
                return "Secure your trip with travel insurance - peace of mind awaits!"

