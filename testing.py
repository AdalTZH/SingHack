import torch
import sounddevice as sd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

def record_audio(duration=5, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), 
                        samplerate=sample_rate, 
                        channels=1, 
                        dtype='float32')
    sd.wait()
    print("Recording finished!")
    return audio_data.flatten()

def process_audio(model, processor, audio_array, query, device):
    """Process audio with a specific query"""
    prompt_template = "Instruction: {query} \nFollow the text instruction based on the following audio: <SpeechHere>"
    
    conversation = [[{"role": "user", "content": prompt_template.format(query=query)}]]
    
    chat_prompt = processor.tokenizer.apply_chat_template(
        conversation=conversation,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = processor(text=chat_prompt, audios=[audio_array])
    
    for key, value in inputs.items():
        if isinstance(value, torch.Tensor):
            inputs[key] = inputs[key].to(device)
            if value.dtype == torch.float32:
                inputs[key] = inputs[key].to(torch.bfloat16)
    
    outputs = model.generate(**inputs, max_new_tokens=256)
    generated_ids = outputs[:, inputs['input_ids'].size(1):]
    response = processor.batch_decode(generated_ids, skip_special_tokens=True)
    
    return response[0]

# Load model ONCE
print("Loading model... (this takes time but only happens once)")
repo_id = "MERaLiON/MERaLiON-2-3B"
device = "cuda"

processor = AutoProcessor.from_pretrained(repo_id, trust_remote_code=True)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    repo_id,
    use_safetensors=True,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
).to(device)
print("Model loaded! Ready to record.\n")

# Record and process
while True:
    input("Press Enter to start recording (or Ctrl+C to quit)...")
    
    # Record audio once
    audio_array = record_audio(duration=10, sample_rate=16000)
    
    print("\nProcessing transcription...")
    transcription = process_audio(
        model, processor, audio_array, 
        "Please transcribe this speech.", 
        device
    )
    
    print("\nProcessing emotion...")
    emotion = process_audio(
        model, processor, audio_array, 
        "What is the emotion of the speaker in one word", 
        device
    )
    
    print(f"\n{'='*50}")
    print(f"Transcription: {transcription}")
    print(f"Emotion: {emotion}")
    print(f"{'='*50}\n")