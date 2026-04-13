from PIL import Image
from typing import Optional
import logging
from transformers import pipeline, BitsAndBytesConfig
import torch

logger = logging.getLogger(__name__)

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

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    vlm_pipe = pipeline(
        "image-text-to-text",
        model="Qwen/Qwen3-VL-8B-Instruct",
        model_kwargs={
            "quantization_config": bnb_config,
            "device_map": "auto"
        }
    )

    logger.info("VLM loaded with 4-bit quantization")


if _is_enabled():
    _init_vlm_pipe()


# 🔥 Extract ONLY text (prevents JSON crash)
def _extract_text(resp) -> str:
    try:
        if isinstance(resp, list) and len(resp) > 0:
            first = resp[0]

            if isinstance(first, dict):

                # Standard HF output
                if "generated_text" in first:
                    return str(first["generated_text"])

                # Qwen chat-style output
                if "content" in first:
                    content = first["content"]

                    if isinstance(content, list):
                        for item in content:
                            if (
                                isinstance(item, dict)
                                and item.get("type") == "text"
                            ):
                                return str(item.get("text", ""))

                    if isinstance(content, str):
                        return content

                # fallback keys
                for key in ("text", "output", "output_text"):
                    if key in first:
                        return str(first[key])

            if isinstance(first, str):
                return first

        if isinstance(resp, str):
            return resp

    except Exception as e:
        logger.error("Failed to extract text: %s", e)

    return str(resp)


def generate_response(image_path: str, question: str) -> str:
    if not _is_enabled():
        return "Models are disabled. Enable USE_MODELS."

    if vlm_pipe is None:
        _init_vlm_pipe()

    try:
        image = Image.open(image_path).convert("RGB")

        # DEBUG: save incoming image
        image.save("debug.jpg")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question},
                ],
            }
        ]

        resp = vlm_pipe(
            messages,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        ) # type: ignore

        logger.info("Raw model response: %s", resp)

        text = _extract_text(resp)

        # 🔥 FINAL SAFETY (prevents Flask crash forever)
        if not isinstance(text, str):
            text = str(text)

        if text.strip() == "":
            return "I couldn't understand the image."

        return text

    except Exception as e:
        logger.exception("VLM generation failed")
        return f"Error generating response: {str(e)}"