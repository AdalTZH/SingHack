"""
Speech Transcriber using MERaLiON-2-3B model
Based on testing.py implementation
"""
import torch
import numpy as np
import wave
import io
import logging
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

from .config import REPO_ID, DEVICE, SAMPLE_RATE

logger = logging.getLogger(__name__)


class SpeechTranscriber:
    """
    Handles audio transcription using MERaLiON-2-3B model
    Model is loaded once and reused for all transcriptions
    """
    
    def __init__(self):
        """Initialize the transcriber and load the model"""
        logger.info(f"Loading model from {REPO_ID}...")
        logger.info(f"Device: {DEVICE}, Sample Rate: {SAMPLE_RATE} Hz")
        
        self.device = DEVICE
        self.sample_rate = SAMPLE_RATE
        
        # Load processor and model (matching testing.py configuration)
        logger.info("Step 1/2: Loading processor...")
        self.processor = AutoProcessor.from_pretrained(REPO_ID, trust_remote_code=True)
        logger.info("Processor loaded!")
        
        logger.info("Step 2/2: Loading model (this may take several minutes on first run)...")
        logger.info("  - Downloading model if not cached (~3GB)")
        logger.info("  - Loading model into memory...")
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            REPO_ID,
            use_safetensors=True,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16
        ).to(self.device)
        
        logger.info("=" * 60)
        logger.info("✅ Model loaded successfully!")
        logger.info(f"✅ Device: {self.device}")
        logger.info(f"✅ Sample Rate: {self.sample_rate} Hz")
        logger.info("=" * 60)
    
    def decode_audio(self, audio_bytes: bytes, format: str = "wav") -> np.ndarray:
        """
        Decode audio bytes to numpy array
        
        Args:
            audio_bytes: Raw audio bytes
            format: Audio format (wav, webm, etc.)
            
        Returns:
            numpy array of audio samples (float32, mono, 16kHz)
        """
        try:
            if format.lower() == "wav":
                # Decode WAV file
                audio_io = io.BytesIO(audio_bytes)
                with wave.open(audio_io, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    audio_data = wav_file.readframes(frames)
                    
                    # Convert to numpy array
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # Convert to float32 and normalize
                    audio_array = audio_array.astype(np.float32) / 32768.0
                    
                    # Resample if needed (simple linear interpolation for now)
                    if sample_rate != self.sample_rate:
                        # Simple resampling (for production, use librosa or scipy)
                        ratio = self.sample_rate / sample_rate
                        indices = np.round(np.arange(0, len(audio_array), 1/ratio)).astype(int)
                        indices = indices[indices < len(audio_array)]
                        audio_array = audio_array[indices]
                    
                    # Ensure mono
                    if len(audio_array.shape) > 1:
                        audio_array = np.mean(audio_array, axis=1)
                    
                    return audio_array.flatten()
            
            elif format.lower() in ["webm", "ogg"]:
                # WebM/OGG formats require additional libraries
                # Try to use pydub if available, otherwise raise error
                try:
                    from pydub import AudioSegment
                    from pydub.utils import which
                    
                    # Check if ffmpeg is available
                    if not which("ffmpeg"):
                        raise ValueError("ffmpeg not found. Please install ffmpeg to support WebM/OGG formats.")
                    
                    # Load audio using pydub
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format.lower())
                    
                    # Convert to mono and 16kHz
                    audio_segment = audio_segment.set_channels(1)
                    audio_segment = audio_segment.set_frame_rate(self.sample_rate)
                    
                    # Convert to numpy array
                    audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                    
                    # Normalize to [-1, 1]
                    if audio_segment.sample_width == 2:
                        audio_array = audio_array / 32768.0
                    elif audio_segment.sample_width == 4:
                        audio_array = audio_array / 2147483648.0
                    else:
                        audio_array = audio_array / (2 ** (audio_segment.sample_width * 8 - 1))
                    
                    return audio_array.flatten()
                    
                except ImportError:
                    raise ValueError(
                        f"Format {format} requires pydub library. "
                        "Install with: pip install pydub"
                    )
                except Exception as e:
                    raise ValueError(f"Failed to decode {format} audio: {e}")
            
            elif format.lower() == "mp3":
                # MP3 also requires pydub/ffmpeg
                raise ValueError(
                    "MP3 format requires pydub and ffmpeg. "
                    "Please convert to WAV first or install: pip install pydub && install ffmpeg"
                )
            
            else:
                raise ValueError(f"Unsupported audio format: {format}")
                
        except Exception as e:
            logger.error(f"Error decoding audio: {e}")
            raise ValueError(f"Failed to decode audio: {e}")
    
    def transcribe(self, audio_array: np.ndarray) -> str:
        """
        Transcribe audio array to text
        
        Args:
            audio_array: numpy array of audio samples (float32, mono, 16kHz)
            
        Returns:
            Transcribed text
        """
        try:
            # Use the same prompt template as testing.py
            query = "Please transcribe this speech."
            prompt_template = "Instruction: {query} \nFollow the text instruction based on the following audio: <SpeechHere>"
            
            conversation = [[{"role": "user", "content": prompt_template.format(query=query)}]]
            
            chat_prompt = self.processor.tokenizer.apply_chat_template(
                conversation=conversation,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Process audio
            inputs = self.processor(text=chat_prompt, audios=[audio_array])
            
            # Move to device and convert dtype
            for key, value in inputs.items():
                if isinstance(value, torch.Tensor):
                    inputs[key] = inputs[key].to(self.device)
                    if value.dtype == torch.float32:
                        inputs[key] = inputs[key].to(torch.bfloat16)
            
            # Generate transcription
            outputs = self.model.generate(**inputs, max_new_tokens=256)
            generated_ids = outputs[:, inputs['input_ids'].size(1):]
            response = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            
            return response[0].strip()
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise ValueError(f"Transcription failed: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'processor'):
            del self.processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Transcriber cleaned up")

