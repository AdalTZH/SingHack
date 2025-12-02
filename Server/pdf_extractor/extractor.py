"""
PDF Text Extraction Module
Handles text extraction from PDF files using PyPDF2 and pdfplumber
"""
import logging
from typing import Dict, Any, Optional, Tuple
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available. Install it for better PDF support.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available. Install it for better PDF text extraction.")


class PDFExtractor:
    """
    PDF text extraction handler.
    
    Uses multiple libraries for robust text extraction:
    - pdfplumber (primary) - better for text-based PDFs
    - PyPDF2 (fallback) - works with most PDFs
    """
    
    def __init__(self):
        """Initialize the PDF extractor"""
        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            raise RuntimeError(
                "No PDF libraries available. Please install pdfplumber or PyPDF2."
            )
    
    def extract_text(self, pdf_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract text from PDF bytes
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Optional filename for logging
            
        Returns:
            Dictionary containing:
            - success: bool
            - text: extracted text content
            - metadata: PDF metadata (pages, title, author, etc.)
            - error: error message if extraction failed
        """
        result = {
            "success": False,
            "text": None,
            "metadata": {},
            "error": None
        }
        
        try:
            # Try pdfplumber first (better text extraction)
            if PDFPLUMBER_AVAILABLE:
                logger.info("Attempting extraction with pdfplumber...")
                text, metadata = self._extract_with_pdfplumber(pdf_bytes)
                if text or metadata:
                    result["success"] = True
                    result["text"] = text
                    result["metadata"] = metadata
                    logger.info(f"Successfully extracted {len(text)} characters using pdfplumber")
                    return result
            
            # Fallback to PyPDF2
            if PYPDF2_AVAILABLE:
                logger.info("Attempting extraction with PyPDF2...")
                text, metadata = self._extract_with_pypdf2(pdf_bytes)
                if text or metadata:
                    result["success"] = True
                    result["text"] = text
                    result["metadata"] = metadata
                    logger.info(f"Successfully extracted {len(text)} characters using PyPDF2")
                    return result
            
            # If both methods failed or returned empty
            result["error"] = "Failed to extract text from PDF. The PDF might be empty or image-based."
            logger.warning("Both extraction methods failed or returned empty text")
            
        except Exception as e:
            error_msg = f"Error extracting text from PDF: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            result["error"] = error_msg
        
        return result
    
    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text using pdfplumber (better for text-based PDFs)
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (text, metadata)
        """
        text_parts = []
        metadata = {
            "method": "pdfplumber",
            "pages": 0
        }
        
        pdf_file = io.BytesIO(pdf_bytes)
        
        with pdfplumber.open(pdf_file) as pdf:
            metadata["pages"] = len(pdf.pages)
            
            # Extract metadata from PDF
            if pdf.metadata:
                metadata["title"] = pdf.metadata.get("Title", "")
                metadata["author"] = pdf.metadata.get("Author", "")
                metadata["subject"] = pdf.metadata.get("Subject", "")
                metadata["creator"] = pdf.metadata.get("Creator", "")
                metadata["producer"] = pdf.metadata.get("Producer", "")
                metadata["creation_date"] = str(pdf.metadata.get("CreationDate", ""))
                metadata["modification_date"] = str(pdf.metadata.get("ModDate", ""))
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"\n--- Page {page_num} ---\n")
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
        
        full_text = "\n".join(text_parts)
        return full_text, metadata
    
    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text using PyPDF2 (fallback method)
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (text, metadata)
        """
        text_parts = []
        metadata = {
            "method": "pypdf2",
            "pages": 0
        }
        
        pdf_file = io.BytesIO(pdf_bytes)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata["pages"] = len(pdf_reader.pages)
            
            # Extract metadata
            if pdf_reader.metadata:
                metadata["title"] = pdf_reader.metadata.get("/Title", "")
                metadata["author"] = pdf_reader.metadata.get("/Author", "")
                metadata["subject"] = pdf_reader.metadata.get("/Subject", "")
                metadata["creator"] = pdf_reader.metadata.get("/Creator", "")
                metadata["producer"] = pdf_reader.metadata.get("/Producer", "")
                metadata["creation_date"] = str(pdf_reader.metadata.get("/CreationDate", ""))
                metadata["modification_date"] = str(pdf_reader.metadata.get("/ModDate", ""))
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"\n--- Page {page_num} ---\n")
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
        
        except PyPDF2.errors.PdfReadError as e:
            raise Exception(f"Invalid PDF file: {str(e)}")
        
        full_text = "\n".join(text_parts)
        return full_text, metadata
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file path
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extraction results
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            return self.extract_text(pdf_bytes, filename=file_path)
        except Exception as e:
            return {
                "success": False,
                "text": None,
                "metadata": {},
                "error": f"Error reading file: {str(e)}"
            }

