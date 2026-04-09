from transformers import ImageTextToTextPipeline, pipeline
from PIL import Image

vlm_pipe : ImageTextToTextPipeline = pipeline("image-text-to-text", model="Qwen/Qwen3-VL-8B-Instruct")

def generate_response(image_path : str, question : str) -> str:
    image = Image.open(image_path).convert("RGB")
    response = vlm_pipe(image=image, text=question)
    return response[0]['generated_text']