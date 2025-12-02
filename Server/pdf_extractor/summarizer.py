"""
PDF Text Summarizer Module
Uses OpenAI GPT models to generate detailed summaries of extracted PDF text
"""
import logging
from typing import Dict, Any, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install it for summarization features.")


class PDFSummarizer:
    """
    PDF text summarizer using OpenAI GPT models.
    
    Generates detailed summaries of PDF content with configurable detail levels.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the PDF summarizer
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        if not OPENAI_AVAILABLE:
            raise RuntimeError(
                "OpenAI library not available. Install with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"PDF Summarizer initialized with model: {self.model}")
    
    def summarize(
        self, 
        text: str, 
        detail_level: str = "detailed",
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a detailed summary of the PDF text
        
        Args:
            text: Extracted text from PDF
            detail_level: Level of detail - "brief", "detailed", or "comprehensive"
            max_length: Maximum length of summary in words (optional)
        
        Returns:
            Dictionary containing:
            - success: bool
            - summary: Generated summary text
            - detail_level: The detail level used
            - token_count: Approximate token count
            - error: error message if summarization failed
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "No text provided for summarization"
            }
        
        try:
            # Determine system prompt based on detail level
            detail_prompts = {
                "brief": "Provide a brief, concise summary highlighting only the most important points.",
                "detailed": "Provide a detailed summary covering all major sections, key points, and important details.",
                "comprehensive": "Provide a comprehensive summary with extensive detail, covering all aspects, sections, and nuances of the content."
            }
            
            detail_instruction = detail_prompts.get(
                detail_level.lower(), 
                detail_prompts["detailed"]
            )
            
            # Build the prompt
            system_prompt = f"""You are an expert document summarizer. Your task is to analyze the provided text and create a well-structured, informative summary.

{detail_instruction}

Guidelines:
- Identify the main topics and themes
- Highlight key information, facts, and data points
- Maintain logical structure and flow
- Use clear, professional language
- Organize information into sections if appropriate
- Include important dates, numbers, and specific details when relevant
- Preserve critical context and relationships between concepts
"""
            
            # Truncate text if it's too long (OpenAI has token limits)
            # GPT-4o-mini can handle ~128k tokens, but we'll be conservative
            max_chars = 200000  # ~50k tokens for input, leaving room for output
            document_text = text[:max_chars] if len(text) > max_chars else text
            
            user_prompt = f"""Please summarize the following document text:

{document_text}

Provide a well-structured summary that captures the essential information and key points."""
            
            if len(text) > max_chars:
                logger.warning(f"Text truncated from {len(text)} to {max_chars} characters for summarization")
            
            # Generate summary
            logger.info(f"Generating {detail_level} summary using {self.model}...")
            logger.info(f"Input text length: {len(document_text)} characters")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual summaries
                max_tokens=4000 if detail_level == "comprehensive" else 2000
            )
            
            summary = response.choices[0].message.content
            
            # Apply max_length constraint if specified
            if max_length:
                words = summary.split()
                if len(words) > max_length:
                    summary = " ".join(words[:max_length]) + "..."
                    logger.info(f"Summary truncated to {max_length} words")
            
            logger.info(f"Summary generated successfully ({len(summary)} characters)")
            
            return {
                "success": True,
                "summary": summary,
                "detail_level": detail_level,
                "token_count": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "input_length": len(document_text),
                "summary_length": len(summary),
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            return {
                "success": False,
                "error": error_msg
            }
    
    def summarize_with_structure(
        self,
        text: str,
        structure_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured summary with specific sections
        
        Args:
            text: Extracted text from PDF
            structure_template: Optional template for summary structure
        
        Returns:
            Dictionary containing structured summary
        """
        default_structure = """Please provide a structured summary with the following sections:
1. Overview/Executive Summary
2. Main Topics/Content Areas
3. Key Points and Details
4. Important Dates, Numbers, or Facts
5. Conclusions or Recommendations (if applicable)"""
        
        structure = structure_template or default_structure
        
        try:
            system_prompt = """You are an expert document analyst. Analyze the provided document and create a structured, comprehensive summary organized into clear sections."""
            
            user_prompt = f"""Analyze the following document and provide a structured summary:

{structure}

Document text:
{text[:200000]}"""  # Truncate if too long
            
            logger.info("Generating structured summary...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            summary = response.choices[0].message.content
            
            return {
                "success": True,
                "summary": summary,
                "structure": structure,
                "token_count": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error generating structured summary: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

