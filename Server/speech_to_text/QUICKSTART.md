# Speech-to-Text Server Quick Start

## Prerequisites

1. **Python 3.8+** installed
2. **CUDA-capable GPU** (recommended) or CPU
3. **FFmpeg** (for WebM/OGG support) - optional but recommended
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

## Installation

1. Navigate to the speech-to-text directory:
```bash
cd Server/speech_to_text
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install FFmpeg for WebM/OGG support:
   - See Prerequisites above

## Configuration

Edit `config.py` if needed:
- `SERVER_PORT`: Default is 8005
- `DEVICE`: Change to `"cpu"` if no GPU available
- `SAMPLE_RATE`: Default is 16000 Hz (matches testing.py)

## Running the Server

### Option 1: Using the startup script
```bash
cd Server
python start_speech_to_text.py
```

### Option 2: Direct module execution
```bash
cd Server
python -m speech_to_text.server
```

### Option 3: Using uvicorn directly
```bash
cd Server/speech_to_text
uvicorn server:app --host 0.0.0.0 --port 8005
```

The server will:
1. Load the MERaLiON-2-3B model (this takes time on first run)
   - **First run**: Downloads model (~3GB) - can take 10-30 minutes
   - **Subsequent runs**: Loads from cache - takes 1-3 minutes
2. Start listening on `http://localhost:8005`
3. Be ready to accept transcription requests

**Important**: The first run will take a long time because it downloads the model. You'll see TensorFlow warnings - these are normal and can be ignored. The server will start after the model finishes loading.

## Testing

### Health Check
```bash
curl http://localhost:8005/health
```

### Test Transcription (using base64 audio)
```bash
# First, encode a WAV file to base64
# Then send POST request:
curl -X POST http://localhost:8005/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "base64_encoded_audio_here", "format": "wav"}'
```

## Integration with Extension

The extension is already configured to use this server. Make sure:
1. Server is running on `http://localhost:8005`
2. Extension config.js has `SPEECH_TO_TEXT_URL: 'http://localhost:8005'`

## Troubleshooting

### Model Loading Takes Too Long
- First load downloads the model (~3GB)
- Subsequent loads are faster (model cached)
- Consider using GPU for faster inference

### CUDA Out of Memory
- Reduce batch size or use CPU
- Change `DEVICE` to `"cpu"` in `config.py`

### WebM/OGG Not Supported
- Install FFmpeg (see Prerequisites)
- Or convert audio to WAV in the browser (already implemented)

### Port Already in Use
- Change `SERVER_PORT` in `config.py`
- Update extension `config.js` with new port

