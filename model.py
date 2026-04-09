from PIL import Image
from typing import Optional

# Lazily-initialized pipeline instance. We avoid constructing the heavy model
# at import time unless `config.USE_MODELS` is enabled.
vlm_pipe: Optional[object] = None

def _is_enabled() -> bool:
    try:
        import config
        return getattr(config, "USE_MODELS", False)
    except Exception:
        return False

def _init_vlm_pipe() -> None:
    global vlm_pipe
    if vlm_pipe is not None:
        return
    from transformers import pipeline
    vlm_pipe = pipeline("image-text-to-text", model="Qwen/Qwen3-VL-8B-Instruct")

# Initialize the pipeline at import-time only when explicitly enabled.
if _is_enabled():
    _init_vlm_pipe()

def generate_response(image_path: str, question: str) -> str:
    if not _is_enabled():
        return "Models are disabled. Enable with ENABLE_MODELS environment variable."
    if vlm_pipe is None:
        _init_vlm_pipe()
    image = Image.open(image_path).convert("RGB")
    response = vlm_pipe(image=image, text=question) # type: ignore
    return response[0]["generated_text"]