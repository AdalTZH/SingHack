# PDF Text Extraction Service - Setup Guide

## Overview

A complete PDF text extraction system has been implemented with:
1. **Backend Server**: FastAPI-based PDF text extraction service
2. **Frontend Integration**: Updated DocumentUpload component to send PDFs to backend
3. **Configuration**: Added PDF extractor URL to extension config

## Architecture

### Backend Service (`Server/pdf_extractor/`)

- **`extractor.py`**: Core PDF extraction logic using pdfplumber and PyPDF2
- **`server.py`**: FastAPI server with `/extract` endpoint
- **`config.py`**: Server configuration (host, port, CORS, file limits)
- **`requirements.txt`**: Dependencies (FastAPI, pdfplumber, PyPDF2, etc.)
- **`README.md`**: Detailed documentation

### Frontend Updates

- **`Extension/src/components/DocumentUpload.tsx`**: 
  - Updated to send PDF files to backend
  - Shows processing status for each file
  - Displays extraction results and errors
  - Handles multiple PDF uploads

- **`Extension/config.js`**: Added PDF_EXTRACTOR_URL configuration

## Installation

### 1. Install Backend Dependencies

```bash
cd Server/pdf_extractor
pip install -r requirements.txt
```

### 2. Start the PDF Extractor Server

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

### 3. Verify Server is Running

```bash
curl http://localhost:8007/health
```

You should see:
```json
{
  "status": "healthy",
  "extractor_loaded": true,
  "max_file_size_mb": 50.0,
  "allowed_file_types": ["application/pdf"]
}
```

## Usage

### From the Extension

1. Open the extension and navigate to the Document Upload screen
2. Drag and drop PDF files or click to browse
3. Click "Continue" to process the files
4. The component will:
   - Show processing status for each file
   - Display extracted text length and page count
   - Show errors if extraction fails
   - Call `onComplete()` when all files are processed successfully

### API Endpoints

#### Extract Text from PDF

```bash
POST http://localhost:8007/extract
Content-Type: multipart/form-data

Body:
  pdf_file: <PDF file>
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
    "creation_date": "...",
    ...
  },
  "file_name": "document.pdf",
  "file_size": 123456,
  "error": null
}
```

### Example: Direct API Call

```python
import requests

with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8007/extract',
        files={'pdf_file': f}
    )
    
result = response.json()
if result['success']:
    print(f"Extracted {len(result['text'])} characters")
    print(f"Pages: {result['metadata']['pages']}")
    print(result['text'])
```

## Configuration

### Backend Configuration

Edit `Server/pdf_extractor/config.py` or set environment variables:

- `PDF_EXTRACTOR_HOST`: Server host (default: `0.0.0.0`)
- `PDF_EXTRACTOR_PORT`: Server port (default: `8007`)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 50 MB)

### Frontend Configuration

The PDF extractor URL can be configured via:

1. **Environment Variable** (for Vite builds):
   ```
   VITE_PDF_EXTRACTOR_URL=http://localhost:8007
   ```

2. **Default**: Falls back to `http://localhost:8007` if not set

## Features

### ✅ Implemented

- PDF text extraction using pdfplumber (primary) and PyPDF2 (fallback)
- Metadata extraction (title, author, pages, dates, etc.)
- File validation (type, size)
- Error handling and user feedback
- Multi-file upload support
- Processing status indicators
- CORS support for extension compatibility

### 🔄 Future Enhancements

- OCR support for scanned/image-based PDFs
- Image extraction from PDFs
- Batch processing endpoint
- Progress tracking for large files
- Password-protected PDF support
- Text extraction from other formats (DOCX, etc.)

## Error Handling

The service handles various error conditions:

- **Invalid file type**: Only PDF files are accepted
- **File size limits**: Maximum 50 MB (configurable)
- **Empty/corrupted PDFs**: Returns appropriate error messages
- **Image-only PDFs**: Returns error if no text is extractable
- **Network errors**: Frontend shows user-friendly error messages

## Testing

### Test with curl

```bash
# Health check
curl http://localhost:8007/health

# Extract text from PDF
curl -X POST "http://localhost:8007/extract" \
  -F "pdf_file=@/path/to/test.pdf"
```

### Test from Extension

1. Start the PDF extractor server
2. Open the extension
3. Upload a PDF file through the DocumentUpload component
4. Verify text extraction and metadata display

## Troubleshooting

### Server won't start

- Check if port 8007 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### Text extraction fails

- Verify the PDF is not password-protected
- Check if PDF is image-only (requires OCR - not yet implemented)
- Review server logs for detailed error messages

### Frontend can't connect

- Verify server is running on port 8007 (or configured port)
- Check CORS configuration in `config.py`
- Verify PDF extractor URL in extension config
- Check browser console for network errors

## File Structure

```
Server/
  pdf_extractor/
    __init__.py          # Package initialization
    config.py            # Server configuration
    extractor.py         # PDF extraction logic
    server.py            # FastAPI server
    requirements.txt     # Dependencies
    README.md            # Detailed documentation
  start_pdf_extractor.py # Startup script

Extension/
  src/
    components/
      DocumentUpload.tsx # Updated upload component
  config.js              # Extension config (updated)
```

## Notes

- The service uses pdfplumber as the primary extraction method for better text quality
- PyPDF2 is used as a fallback for compatibility
- Maximum file size is set to 50 MB by default (configurable)
- The frontend currently only supports PDF files for text extraction
- Extracted text is stored in component state but can be passed to parent via callback

