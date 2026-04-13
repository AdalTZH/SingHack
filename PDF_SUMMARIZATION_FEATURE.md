# PDF Summarization Feature

## Overview

The PDF Extractor server now includes AI-powered summarization capabilities using OpenAI GPT models. This feature allows you to generate detailed, intelligent summaries of PDF documents after text extraction.

## Features Added

### 1. **PDF Summarizer Module** (`summarizer.py`)
- Uses OpenAI GPT models for text summarization
- Supports three detail levels: brief, detailed, comprehensive
- Can generate structured summaries with organized sections
- Handles long documents with automatic text truncation
- Configurable temperature for consistent, factual summaries

### 2. **Enhanced Extraction Endpoint**
- `/extract` endpoint now supports optional summarization
- Query parameters:
  - `summarize`: Boolean flag to enable summarization
  - `detail_level`: "brief", "detailed", or "comprehensive"
- Returns extracted text, metadata, and AI-generated summary

### 3. **New Summarization Endpoint**
- `/summarize` endpoint for summarizing already-extracted text
- Accepts text input and summarization options
- Supports structured summaries with organized sections

### 4. **Configuration Options**
- `OPENAI_API_KEY`: OpenAI API key (required for summarization)
- `PDF_SUMMARIZER_MODEL`: Model to use (default: `gpt-4o-mini`)
- `PDF_SUMMARIZE_BY_DEFAULT`: Auto-generate summaries on extraction (default: `false`)

## Installation

1. Install dependencies:
```bash
cd Server/pdf_extractor
pip install -r requirements.txt
```

2. Set OpenAI API key:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

Or add to `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage Examples

### Extract Text with Summary

```bash
curl -X POST "http://localhost:8007/extract?summarize=true&detail_level=detailed" \
  -F "pdf_file=@document.pdf"
```

### Summarize Existing Text

```bash
curl -X POST "http://localhost:8007/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "detail_level": "detailed",
    "structured": false
  }'
```

### Python Example

```python
import requests

# Extract and summarize PDF
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8007/extract',
        files={'pdf_file': f},
        params={'summarize': True, 'detail_level': 'detailed'}
    )

result = response.json()
if result['success']:
    print("Extracted Text:")
    print(result['text'][:500])  # First 500 chars
    
    if result.get('summary'):
        print("\nSummary:")
        print(result['summary'])
        print(f"\nSummary Metadata: {result.get('summary_metadata')}")
```

## Detail Levels

### Brief
- Concise summary
- Highlights only most important points
- Best for quick overviews

### Detailed (Default)
- Comprehensive summary
- Covers all major sections and key points
- Best for most use cases

### Comprehensive
- Extensive detail
- Covers all aspects and nuances
- Best for in-depth analysis

## Structured Summaries

When `structured: true` is set, summaries are organized into sections:

1. Overview/Executive Summary
2. Main Topics/Content Areas
3. Key Points and Details
4. Important Dates, Numbers, or Facts
5. Conclusions or Recommendations (if applicable)

## Response Format

### Extraction with Summary

```json
{
  "success": true,
  "text": "Full extracted text...",
  "metadata": {
    "pages": 10,
    "method": "pdfplumber",
    ...
  },
  "summary": "AI-generated summary...",
  "summary_metadata": {
    "detail_level": "detailed",
    "token_count": 1500,
    "summary_length": 2500
  },
  "file_name": "document.pdf",
  "file_size": 123456
}
```

### Summarization Only

```json
{
  "success": true,
  "summary": "Generated summary text...",
  "detail_level": "detailed",
  "token_count": 1500
}
```

## Error Handling

The summarization feature is designed to be non-blocking:
- If summarization fails, text extraction still succeeds
- Errors are logged but don't break the extraction process
- Server gracefully handles missing OpenAI API key
- Clear error messages guide configuration

## Performance Considerations

- **Token Limits**: Documents are automatically truncated to ~200k characters (conservative limit)
- **Processing Time**: Summarization adds ~2-10 seconds depending on document length
- **Cost**: Uses OpenAI API - costs vary by model and document length
- **Caching**: Consider caching summaries for frequently accessed documents

## Configuration

### Environment Variables

```bash
# Required for summarization
OPENAI_API_KEY=your_key_here

# Optional configuration
PDF_SUMMARIZER_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo, etc.
PDF_SUMMARIZE_BY_DEFAULT=false    # Set to true to auto-summarize
```

### Default Settings

- Model: `gpt-4o-mini` (cost-effective, good quality)
- Temperature: `0.3` (for consistent, factual summaries)
- Max tokens: `2000` for detailed, `4000` for comprehensive
- Auto-summarize: `false` (opt-in)

## Integration Notes

- Summarization is optional - server works without OpenAI key
- Health check endpoint shows if summarizer is loaded
- Frontend can request summaries via query parameters
- Backward compatible - existing endpoints still work

## Troubleshooting

### Summarizer not available
- Check if `openai` package is installed
- Verify `OPENAI_API_KEY` is set correctly
- Check server logs for initialization errors

### Summary generation fails
- Verify OpenAI API key is valid
- Check API quota/rate limits
- Review server logs for specific errors
- Ensure document text is not empty

### Long processing times
- Large documents take longer to summarize
- Consider using "brief" detail level for faster results
- Check network connectivity to OpenAI API

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set OpenAI API key: `export OPENAI_API_KEY="your_key"`
3. Start server: `python start_pdf_extractor.py`
4. Test with: `curl http://localhost:8007/health` (should show `summarizer_loaded: true`)


