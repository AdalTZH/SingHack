# PDF Text Extraction Service

A FastAPI-based service for extracting text content from uploaded PDF documents.

## Features

- **Text Extraction**: Extracts text from PDF files using multiple extraction libraries
- **AI-Powered Summarization**: Uses OpenAI GPT models to generate detailed summaries of PDF content
- **Metadata Extraction**: Extracts PDF metadata (title, author, creation date, etc.)
- **Robust Error Handling**: Handles various PDF formats and error conditions
- **File Validation**: Validates file type and size before processing
- **Multi-library Support**: Uses pdfplumber (primary) and PyPDF2 (fallback) for better compatibility
- **Configurable Summary Detail**: Choose between brief, detailed, or comprehensive summaries

## Installation

1. Install dependencies:

```bash
cd Server/pdf_extractor
pip install -r requirements.txt
```

## Configuration

The server can be configured via environment variables or defaults:

- `PDF_EXTRACTOR_HOST`: Server host (default: `0.0.0.0`)
- `PDF_EXTRACTOR_PORT`: Server port (default: `8007`)
- `OPENAI_API_KEY`: OpenAI API key for summarization features (required for summarization)
- `PDF_SUMMARIZER_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)
- `PDF_SUMMARIZE_BY_DEFAULT`: Auto-generate summaries on extraction (default: `false`)

## Usage

### Start the Server

From the `Server` directory:

```bash
python start_pdf_extractor.py
```

Or directly:

```bash
cd Server/pdf_extractor
python -m pdf_extractor.server
```

The server will start on `http://localhost:8007` by default.

### API Endpoints

#### Health Check

```bash
GET /health
```

Returns server status and configuration.

#### Extract Text from PDF

```bash
POST /extract
Content-Type: multipart/form-data

File: pdf_file (PDF file)
Query Parameters:
  - summarize: bool (optional, default: false) - Generate AI summary
  - detail_level: str (optional, default: "detailed") - Summary detail: "brief", "detailed", or "comprehensive"
```

**Response:**
```json
{
  "success": true,
  "text": "Extracted text content...",
  "metadata": {
    "method": "pdfplumber",
    "pages": 5,
    "title": "Document Title",
    "author": "Author Name",
    ...
  },
  "summary": "AI-generated summary of the document...",
  "summary_metadata": {
    "detail_level": "detailed",
    "token_count": 1500,
    "summary_length": 2500
  },
  "file_name": "document.pdf",
  "file_size": 123456,
  "error": null
}
```

#### Summarize Text

```bash
POST /summarize
Content-Type: application/json

Body:
{
  "text": "Text to summarize...",
  "detail_level": "detailed",  // Optional: "brief", "detailed", or "comprehensive"
  "structured": false  // Optional: Generate structured summary with sections
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Generated summary text...",
  "detail_level": "detailed",
  "token_count": 1500,
  "error": null
}
```

### Example Usage

#### Using curl

```bash
# Extract text only
curl -X POST "http://localhost:8007/extract" \
  -F "pdf_file=@/path/to/document.pdf"

# Extract text with summary
curl -X POST "http://localhost:8007/extract?summarize=true&detail_level=detailed" \
  -F "pdf_file=@/path/to/document.pdf"

# Summarize existing text
curl -X POST "http://localhost:8007/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here...", "detail_level": "detailed"}'
```

#### Using Python

```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8007/extract',
        files={'pdf_file': f}
    )
    
result = response.json()
if result['success']:
    print(result['text'])
else:
    print(f"Error: {result['error']}")
```

## Architecture

- **extractor.py**: Core PDF text extraction logic using pdfplumber and PyPDF2
- **summarizer.py**: AI-powered text summarization using OpenAI GPT models
- **server.py**: FastAPI server with endpoints for PDF upload, text extraction, and summarization
- **config.py**: Configuration management for server settings and OpenAI integration

## Error Handling

The service handles various error conditions:

- Invalid file types (non-PDF files)
- File size limits (default: 50 MB)
- Empty or corrupted PDF files
- PDFs with no extractable text (image-only PDFs)

## Limitations

- Currently supports text extraction only (no OCR for scanned PDFs)
- Image extraction from PDFs is not implemented
- Maximum file size: 50 MB (configurable)

## Summarization Features

### Detail Levels

- **Brief**: Concise summary highlighting only the most important points
- **Detailed**: Comprehensive summary covering all major sections and key points (default)
- **Comprehensive**: Extensive summary with full detail on all aspects

### Structured Summaries

Set `structured: true` in the `/summarize` endpoint to get a summary organized into sections:
- Overview/Executive Summary
- Main Topics/Content Areas
- Key Points and Details
- Important Dates, Numbers, or Facts
- Conclusions or Recommendations (if applicable)

## Future Enhancements

- OCR support for scanned/image-based PDFs
- Image extraction from PDFs
- Batch processing for multiple PDFs
- Progress tracking for large files
- Support for password-protected PDFs
- Custom summary prompts

