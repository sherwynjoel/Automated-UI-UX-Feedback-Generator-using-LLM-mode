# feedback_generator_inference.py
import os
from PIL import Image
import uuid
import json
from feedback_generator_heuristics import heuristics_prompt_block

OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def preprocess_and_save_image(pil_image, max_size=1024):
    img = pil_image.convert("RGB")
    w,h = img.size
    scale = min(max_size/w, max_size/h, 1.0)
    if scale < 1.0:
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    filename = os.path.join(OUTPUTS_DIR, f"screenshot_{uuid.uuid4().hex[:8]}.png")
    img.save(filename, format="PNG")
    return filename

def build_prompt_for_model(image_path):
    # NOTE: many multimodal wrappers expect image tensors, not file paths.
    # This prompt is a generic instruction for *text-only* llama backends.
    # When you integrate the real BakLLaVA multimodal loader, pass the image tensors per that loader's API.
    intro = heuristics_prompt_block()
    extra = f"\n\nScreenshot file path: {image_path}\n\nDescribe the UI in a few short sentences, then produce the requested JSON."
    return intro + extra

def analyze_image(pil_image, model, as_json=True):
    """
    pil_image: PIL.Image
    model: object with a .generate(prompt) -> str
    """
    image_path = preprocess_and_save_image(pil_image)
    prompt = build_prompt_for_model(image_path)
    raw = model.generate(prompt)
    # Try to parse JSON-like output; if parsing fails, return raw text.
    if as_json:
        try:
            parsed = json.loads(raw)
            return parsed
        except Exception:
            return {"raw": raw}
    else:
        return raw
