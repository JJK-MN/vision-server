from transformers import pipeline
import torch

VoicePipeline = pipeline(
    "automatic-speech-recognition",
    model="distil-whisper/distil-large-v3.5",
    device=0,  # use GPU
    torch_dtype=torch.float16  # reduces VRAM + speeds up
)

def transcribe_audio(audio_path: str) -> str:
    result = VoicePipeline(
        audio_path,
        chunk_length_s=30,   # important for long audio
        batch_size=8         # tweak based on VRAM
    )
    return result["text"] # type: ignore