# feedback_generator_app.py
import gradio as gr
import yaml
from feedback_generator_model import load_model_from_config, load_config
from feedback_generator_inference import analyze_image
from feedback_generator_utils import write_json_to_file, save_report_pdf
import os

cfg = load_config()
model = load_model_from_config(cfg)

def run_feedback(pil_img):
    # runs inference and returns text + saves JSON/PDF
    result = analyze_image(pil_img, model, as_json=True)
    # Save outputs
    import time, uuid
    name = f"report_{uuid.uuid4().hex[:8]}"
    json_path = os.path.join("outputs", name + ".json")
    pdf_path = os.path.join("outputs", name + ".pdf")
    write_json_to_file(result, json_path)
    save_report_pdf(result, pdf_path)
    # Return a simple display string and links to files (local paths)
    return f"Saved JSON: {json_path}\nSaved PDF: {pdf_path}\n\nModel output (truncated):\n{str(result)[:300]}"

demo = gr.Interface(
    fn=run_feedback,
    inputs=gr.Image(type="pil", label="Upload screenshot"),
    outputs=gr.Textbox(label="Result"),
    title="Feedback Generator (BakLLaVA local)",
    description="Uploads a screenshot and returns UX feedback (mock or llama.cpp backend)."
)

if __name__ == "__main__":
    demo.launch(share=True)
