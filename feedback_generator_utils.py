# feedback_generator_utils.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os

def write_json_to_file(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def save_report_pdf(json_obj, out_pdf_path):
    c = canvas.Canvas(out_pdf_path, pagesize=letter)
    width, height = letter
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 11)
    text.textLines("UX Feedback Report\n")
    text.textLines("")
    # Pretty print JSON lines
    import json
    lines = json.dumps(json_obj, indent=2).splitlines()
    for line in lines:
        text.textLine(line[:1000])  # trim if too long
    c.drawText(text)
    c.showPage()
    c.save()
    return out_pdf_path
