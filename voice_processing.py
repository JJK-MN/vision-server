from typing import Optional

# Lazily initialize the speech-recognition pipeline only when enabled.
_voice_pipeline: Optional[object] = None

def _is_enabled() -> bool:
    try:
        import config
        return getattr(config, "USE_VOICE", False)
    except Exception:
        return False

def _init_voice_pipeline() -> None:
    global _voice_pipeline
    if _voice_pipeline is not None:
        return
    from transformers import pipeline
    import torch
    _voice_pipeline = pipeline(
        "automatic-speech-recognition",
        model="distil-whisper/distil-large-v3.5",
        device=0,  # use GPU
        torch_dtype=torch.float16  # reduces VRAM + speeds up
    )

if _is_enabled():
    _init_voice_pipeline()

def transcribe_audio(audio_path: str) -> str:
    if not _is_enabled():
        return ""
    if _voice_pipeline is None:
        _init_voice_pipeline()
    
    result = _voice_pipeline(
        audio_path,
        chunk_length_s=30,   # important for long audio
        batch_size=8         # tweak based on VRAM
    ) # type: ignore
    return result["text"] # type: ignore