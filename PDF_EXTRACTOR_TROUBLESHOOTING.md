# PDF Extractor - Troubleshooting Guide

## 404 Error Fix

If you're getting a 404 error when trying to extract text from PDFs, follow these steps:

### 1. Check if Server is Running

First, verify the server is running on port 8007:

```bash
# Check if port 8007 is in use
netstat -ano | findstr :8007  # Windows
lsof -i :8007  # Mac/Linux

# Or test the health endpoint
curl http://localhost:8007/health
```

### 2. Start the Server

If the server isn't running, start it:

```bash
cd Server
python start_pdf_extractor.py
```

Or directly:

```bash
cd Server/pdf_extractor
python -m pdf_extractor.server
```

You should see output like:
```
INFO: Initializing PDF Text Extraction Server...
INFO: Host: 0.0.0.0, Port: 8007
INFO: Uvicorn running on http://0.0.0.0:8007
```

### 3. Test the Endpoint

Test the extract endpoint directly:

```bash
curl -X POST "http://localhost:8007/extract" \
  -F "pdf_file=@/path/to/test.pdf"
```

### 4. Check Browser Console

Open the browser console (F12) and check:
- Network tab: See the actual request being made
- Console tab: Look for detailed error messages

The updated code now logs:
- The exact URL being called
- Server health check status
- Response status and headers
- Detailed error messages

### 5. Common Issues

#### Issue: "Server is not available"
**Solution**: Start the PDF extractor server on port 8007

#### Issue: "Cannot connect to PDF extractor server"
**Solution**: 
- Verify the server is running
- Check firewall settings
- Ensure port 8007 is not blocked

#### Issue: 404 Not Found
**Possible causes**:
- Server is not running
- Server is running on a different port
- Route is not registered (check server logs)

#### Issue: CORS errors
**Solution**: The server already has CORS configured. If issues persist, check:
- The `ALLOWED_ORIGINS` in `Server/pdf_extractor/config.py`
- Browser console for specific CORS error messages

### 6. Verify Server Routes

Check what routes are available:

```bash
# Visit in browser:
http://localhost:8007/docs
```

This will show the FastAPI Swagger UI with all available endpoints.

### 7. Check Server Logs

When the server starts, it should log:
```
INFO: Initializing PDF Text Extraction Server...
INFO: Host: 0.0.0.0, Port: 8007
INFO: Initializing PDF Text Extractor...
INFO: PDF Extractor initialized successfully!
INFO: Server running on http://0.0.0.0:8007
```

If you see errors, check:
- Missing dependencies (install from `requirements.txt`)
- Port conflicts (another service using port 8007)
- Import errors

### 8. Installation Check

Make sure all dependencies are installed:

```bash
cd Server/pdf_extractor
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- pdfplumber
- PyPDF2
- python-multipart
- python-dotenv

### 9. Quick Test Script

Create a test file `test_pdf_extractor.py`:

```python
import requests

# Test health endpoint
response = requests.get('http://localhost:8007/health')
print("Health check:", response.json())

# Test extract endpoint (if you have a PDF file)
with open('test.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8007/extract',
        files={'pdf_file': f}
    )
    print("Extract response:", response.json())
```

Run it:
```bash
python test_pdf_extractor.py
```

## Still Having Issues?

1. **Check the server logs** - Look for error messages when starting the server
2. **Verify port availability** - Make sure nothing else is using port 8007
3. **Test with curl** - Try the API directly with curl to isolate frontend/backend issues
4. **Check browser network tab** - See the exact request/response being sent
5. **Restart the server** - Sometimes a clean restart helps

## Updated Error Messages

The frontend now provides more detailed error messages:
- "Server is not available" - Health check failed
- "Cannot connect to PDF extractor server" - Network error
- Specific error messages from the server

Check the browser console for detailed logs with `[PDF Extractor]` prefix.


