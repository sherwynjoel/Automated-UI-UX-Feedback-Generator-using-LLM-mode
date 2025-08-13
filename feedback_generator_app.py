# feedback_generator_app.py
import gradio as gr
import os
import uuid
from feedback_generator_model import load_model_from_config, load_config
from feedback_generator_inference import analyze_image
from feedback_generator_utils import write_json_to_file, save_report_pdf
from feedback_generator_enrich import enrich_feedback, NIELSEN_10  # added NIELSEN_10

# Create outputs folder if not exists
os.makedirs("outputs", exist_ok=True)

print("🔹 Step 1: Loading config...")
cfg = load_config()

print("🔹 Step 2: Loading model...")
model = load_model_from_config(cfg)

def run_feedback(pil_img):
    print("✅ Received image, running analysis...")

    try:
        analysis_result = analyze_image(pil_img, model, as_json=True)
    except Exception as e:
        return f"❌ Error running analysis: {e}"

    print("✅ Analysis done")

    # Get JSON result
    out_json = analysis_result.get("result", analysis_result)
    if not isinstance(out_json, dict):
        return "❌ Error: Model output is not a dictionary — PDF export aborted."

    # ✅ Enrich feedback to ensure all heuristics & minimum fixes
    out_json = enrich_feedback(
        out_json,
        min_fixes_per=3,  # guarantee at least 3 fixes per heuristic
        enforce_all_heuristics=True
    )

    screenshot_path = analysis_result.get("screenshot_path", None)

    # File naming
    name = f"report_{uuid.uuid4().hex[:8]}"
    json_path = os.path.join("outputs", name + ".json")
    pdf_path = os.path.join("outputs", name + ".pdf")

    try:
        print("💾 Saving JSON...")
        write_json_to_file(out_json, json_path)
    except Exception as e:
        return f"❌ Error saving JSON: {e}"

    try:
        print("💾 Saving PDF...")
        save_report_pdf(
            out_json,
            pdf_path,
            screenshot_path=screenshot_path,
            logo_path=None,  # Disable logo
            font_path="assets/fonts/DejaVuSans.ttf"
        )
    except Exception as e:
        return f"❌ Error saving PDF: {e}"

    print("✅ All done")
    return f"Saved JSON: {json_path}\nSaved PDF: {pdf_path}\n\nModel output (truncated):\n{str(out_json)[:300]}"

print("🔹 Step 3: Creating Gradio interface...")
demo = gr.Interface(
    fn=run_feedback,
    inputs=gr.Image(type="pil", label="Upload screenshot"),
    outputs=gr.Textbox(label="Result"),
    title="Feedback Generator (BakLLaVA local)",
    description="Uploads a screenshot and returns UX feedback (mock or llama.cpp backend)."
)

if __name__ == "__main__":
    print("🚀 Launching Gradio app...")
    demo.launch(share=True)
