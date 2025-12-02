# Speech-to-Text Server

Separate server for audio transcription using MERaLiON-2-3B model.

## Features

- Audio transcription using MERaLiON-2-3B model
- FastAPI REST API
- Base64 audio input support
- File upload support
- Same configuration as `testing.py`

## Setup

1. Install dependencies:
```bash
cd Server/speech_to_text
pip install -r requirements.txt
```

2. Ensure you have CUDA available (or change `DEVICE` to `"cpu"` in `config.py`)

3. Run the server:
```bash
python -m speech_to_text.server
# Or use the startup script:
python ../start_speech_to_text.py
```

The server will start on `http://localhost:8005` by default.

## API Endpoints

### POST `/transcribe`
Transcribe audio from base64 encoded data.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_string",
  "format": "wav"
}
```

**Response:**
```json
{
  "success": true,
  "text": "Transcribed text here"
}
```

### POST `/transcribe-file`
Transcribe audio from uploaded file.

**Request:** Multipart form data with `audio_file`

**Response:**
```json
{
  "success": true,
  "text": "Transcribed text here"
}
```

### GET `/health`
Health check endpoint.

## Configuration

Edit `config.py` to change:
- Server host/port
- Model device (cuda/cpu)
- Sample rate
- CORS origins



