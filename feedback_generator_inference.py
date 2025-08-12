# feedback_generator_inference.py
import os, io, json, uuid
from PIL import Image
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
    intro = heuristics_prompt_block()
    extra = f"\n\nScreenshot file path: {image_path}\n\nDescribe the UI in short, then produce JSON keyed by the heuristics."
    return intro + extra

def analyze_image(pil_image, model, as_json=True):
    """
    Returns: dict: { "result": <parsed-json-or-raw>, "screenshot_path": <path> }
    """
    # save/resize image
    image_path = preprocess_and_save_image(pil_image)

    # build prompt and call model
    prompt = build_prompt_for_model(image_path)
    raw = model.generate(prompt)  # assumes model.generate returns str

    # parse JSON if possible
    parsed = None
    try:
        parsed = json.loads(raw)
    except Exception:
        # attempt to extract JSON substring — fallback to raw
        parsed = {"raw": raw}

    # ensure result is a dict (heuristics dict expected)
    result = parsed if isinstance(parsed, dict) else {"raw": str(parsed)}
    return {"result": result, "screenshot_path": image_path}
