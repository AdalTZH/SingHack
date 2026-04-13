# Speech-to-Text Integration Guide

## Overview

This integration adds microphone recording and speech-to-text functionality to the extension. Audio is recorded in the browser, sent to a dedicated backend server for transcription, and automatically sent to the chatbot.

## Architecture

```
Extension (Browser) → Background Script → Speech-to-Text Server → Chatbot
     ↓                      ↓                      ↓
  Record Audio      →   Base64 Encode    →   Transcribe    →   Send Message
```

## Components

### 1. Speech-to-Text Server (`Server/speech_to_text/`)
- **Location**: `Server/speech_to_text/`
- **Technology**: FastAPI + MERaLiON-2-3B model
- **Port**: 8005 (default)
- **Endpoints**:
  - `POST /transcribe` - Transcribe base64 audio
  - `POST /transcribe-file` - Transcribe uploaded file
  - `GET /health` - Health check

### 2. Extension Components
- **GlassFAB Component** (`Extension/src/components/GlassFAB.tsx`)
  - Added microphone recording functionality
  - Converts WebM to WAV in browser
  - Sends audio to background script
  
- **Background Script** (`Extension/background.js`)
  - Handles `speech-to-text` message type
  - Forwards audio to speech-to-text server
  - Returns transcription to extension

- **Config** (`Extension/config.js`)
  - Added `SPEECH_TO_TEXT_URL` configuration

## Setup Instructions

### 1. Install Speech-to-Text Server

```bash
cd Server/speech_to_text
pip install -r requirements.txt
```

**Optional**: Install FFmpeg for WebM/OGG support:
- Windows: Download from https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### 2. Configure Extension

Edit `Extension/config.js`:
```javascript
SPEECH_TO_TEXT_URL: 'http://localhost:8005'
```

### 3. Start the Server

```bash
cd Server
python start_speech_to_text.py
```

The server will:
- Load MERaLiON-2-3B model (takes time on first run)
- Start on `http://localhost:8005`
- Be ready for transcription requests

### 4. Test the Integration

1. Open the extension sidebar
2. Click the main FAB button to expand
3. Click the microphone icon
4. Grant microphone permission when prompted
5. Speak into the microphone
6. Click the microphone again to stop recording
7. Transcription will be automatically sent to the chatbot

## How It Works

### Recording Flow

1. **User clicks microphone button** in GlassFAB
2. **Browser requests microphone access** (user grants permission)
3. **MediaRecorder starts recording** at 16kHz, mono
4. **Audio chunks are collected** in memory
5. **User clicks microphone again** to stop
6. **Audio is converted** from WebM to WAV format
7. **Audio is base64 encoded** and sent to background script
8. **Background script forwards** to speech-to-text server
9. **Server transcribes** using MERaLiON-2-3B model
10. **Transcription is returned** to extension
11. **Text is automatically sent** to chatbot via `onSend()`

### Audio Format Handling

- **Recording**: Uses MediaRecorder with WebM/Opus (widely supported)
- **Conversion**: Browser converts WebM to WAV using AudioContext
- **Server**: Accepts WAV format (can also handle WebM with FFmpeg)

## Configuration

### Server Configuration (`Server/speech_to_text/config.py`)

```python
SERVER_PORT = 8005  # Change if needed
DEVICE = "cuda"     # Change to "cpu" if no GPU
SAMPLE_RATE = 16000 # Must match recording sample rate
```

### Extension Configuration (`Extension/config.js`)

```javascript
SPEECH_TO_TEXT_URL: 'http://localhost:8005'
```

## Troubleshooting

### Microphone Not Working
- Check browser permissions (chrome://settings/content/microphone)
- Ensure HTTPS or localhost (required for getUserMedia)
- Check browser console for errors

### Transcription Fails
- Verify server is running: `curl http://localhost:8005/health`
- Check server logs for errors
- Ensure model loaded successfully (check server startup logs)
- Verify audio format is supported (WAV preferred)

### Server Won't Start
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 8005 is available
- For GPU: Ensure CUDA is properly installed

### Model Loading Issues
- First run downloads model (~3GB) - be patient
- Check available disk space
- For CPU: Change `DEVICE = "cpu"` in config.py
- Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

## Browser Permissions

The extension uses the Web Audio API (`getUserMedia`) which:
- **Does NOT require** explicit permissions in manifest.json
- **Will prompt user** for microphone access when first used
- **Requires HTTPS or localhost** (security requirement)

## Performance Notes

- **Model Loading**: ~30-60 seconds on first run (model cached after)
- **Transcription**: ~2-5 seconds per 10 seconds of audio (GPU)
- **CPU Mode**: Slower but works without GPU
- **Memory**: Model uses ~6GB VRAM (GPU) or RAM (CPU)

## Future Improvements

- [ ] Add real-time transcription (streaming)
- [ ] Support for multiple languages
- [ ] Voice activity detection (auto-stop recording)
- [ ] Audio quality indicators
- [ ] Transcription confidence scores



