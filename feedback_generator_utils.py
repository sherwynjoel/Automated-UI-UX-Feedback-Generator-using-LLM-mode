# feedback_generator_utils.py
import os, io, json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, ListFlowable, ListItem, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage, ImageDraw, ImageFont

def write_json_to_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _register_font_if_exists(ttf_path):
    if ttf_path and os.path.exists(ttf_path):
        try:
            pdfmetrics.registerFont(TTFont("CustomSans", ttf_path))
            return "CustomSans"
        except Exception:
            return None
    return None

def _colored_dot_bytes(color_hex="#00AA00", size=24):
    size = int(size)
    img = PILImage.new("RGBA", (size, size), (255,255,255,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((1,1,size-2,size-2), fill=color_hex)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

def annotate_image(input_path, annotations, out_path=None):
    if not input_path or not os.path.exists(input_path):
        return None
    img = PILImage.open(input_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    for i, ann in enumerate(annotations or []):
        bbox = ann.get("bbox")
        label = ann.get("label", f"Issue {i+1}")
        if not bbox:
            continue
        if max(bbox) <= 1.0:
            x1, y1, x2, y2 = int(bbox[0]*w), int(bbox[1]*h), int(bbox[2]*w), int(bbox[3]*h)
        else:
            x1, y1, x2, y2 = map(int, bbox)
        draw.rectangle([x1,y1,x2,y2], outline=(255,0,0,255), width=4)
        ts = draw.textsize(label, font=font)
        draw.rectangle([x1-2,y1-2,x1+ts[0]+6,y1+ts[1]+6], fill=(255,0,0,180))
        draw.text((x1+3,y1+3), label, fill=(255,255,255,255), font=font)
    out_path = out_path or os.path.join("outputs", f"annotated_{os.path.basename(input_path)}")
    img.save(out_path)
    return out_path

def _add_page_number(canvas, doc):
    canvas.saveState()
    footer_text = f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} — Page {doc.page}"
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(letter[0]/2.0, 20, footer_text)
    canvas.restoreState()

def save_report_pdf(json_obj, out_pdf_path, screenshot_path=None, logo_path=None, font_path=None, title="UX Feedback Report"):
    os.makedirs(os.path.dirname(out_pdf_path), exist_ok=True)
    chosen_font = _register_font_if_exists(font_path)
    styles = getSampleStyleSheet()
    normal_name = chosen_font or styles["Normal"].fontName
    styles.add(ParagraphStyle(name="Heading1Custom", parent=styles["Heading1"], fontName=normal_name, fontSize=18, leading=22))
    styles.add(ParagraphStyle(name="Heading2Custom", parent=styles["Heading2"], fontName=normal_name, fontSize=14, leading=18))
    styles.add(ParagraphStyle(name="NormalCustom", parent=styles["Normal"], fontName=normal_name, fontSize=11, leading=14))
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontName=normal_name, fontSize=9, leading=11))

    doc = SimpleDocTemplate(out_pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
    story = []

    # Cover
    if logo_path and os.path.exists(logo_path):
        img = RLImage(logo_path, width=1.1*inch, height=1.1*inch)
        t = Table([[img, Paragraph(f"<b>{title}</b><br/><font size=10>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</font>", styles["Heading1Custom"])]],
                  colWidths=[1.4*inch, 4.8*inch])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(t)
    else:
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading1Custom"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Small"]))
    story.append(Spacer(1, 12))

    # raw fallback
    if isinstance(json_obj, dict) and "raw" in json_obj and len(json_obj)==1:
        story.append(Paragraph("Model output (raw):", styles["Heading2Custom"]))
        story.append(Spacer(1,6))
        story.append(Paragraph(json_obj["raw"].replace("\n","<br/>"), styles["NormalCustom"]))
        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return out_pdf_path

    # counts
    counts = {"Good":0, "Needs improvement":0, "Critical":0, "N/A":0}
    for k,v in (json_obj.items() if isinstance(json_obj, dict) else []):
        if isinstance(v, dict):
            verdict = v.get("verdict","N/A")
            counts[verdict] = counts.get(verdict,0) + 1

    summary_data = [["Verdict", "Count"],
                    ["Good", str(counts.get("Good",0))],
                    ["Needs improvement", str(counts.get("Needs improvement",0))],
                    ["Critical", str(counts.get("Critical",0))]]
    tbl = Table(summary_data, colWidths=[3*inch, 1*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#f0f0f0")),
        ("LINEABOVE",(0,0),(-1,0),1,colors.black),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey)
    ]))
    story.append(Paragraph("Executive Summary", styles["Heading2Custom"]))
    story.append(Spacer(1,6))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # annotate screenshot if annotations exist
    annotated_path = None
    try:
        all_annotations = []
        for hk,hv in json_obj.items():
            if isinstance(hv, dict) and hv.get("annotations"):
                for a in hv["annotations"]:
                    if "label" not in a:
                        a["label"] = hk
                    all_annotations.append(a)
        if screenshot_path and all_annotations:
            annotated_path = annotate_image(screenshot_path, all_annotations)
        elif screenshot_path:
            annotated_path = screenshot_path
    except Exception:
        annotated_path = screenshot_path

    if annotated_path and os.path.exists(annotated_path):
        story.append(Paragraph("Screenshot (annotated)", styles["Heading2Custom"]))
        story.append(Spacer(1,6))
        pil = PILImage.open(annotated_path)
        iw, ih = pil.size
        max_w = 6.5*inch
        ratio = min(max_w/iw, 1.0)
        story.append(RLImage(annotated_path, width=iw*ratio, height=ih*ratio))
        story.append(Spacer(1,12))

    severity_order = {"Critical": 0, "Needs improvement": 1, "Good": 2, "N/A": 3}
    heuristics = list(json_obj.items()) if isinstance(json_obj, dict) else []
    heuristics.sort(key=lambda kv: severity_order.get((kv[1].get("verdict") if isinstance(kv[1], dict) else "N/A"), 3))

    color_map = {"Good":"#2E8B57", "Needs improvement":"#FFA500", "Critical":"#D9463E", "N/A":"#808080"}
    for hk,hv in heuristics:
        if not isinstance(hv, dict):
            continue
        verdict = hv.get("verdict","N/A")
        why = hv.get("why","")
        fixes = hv.get("fix", []) or []

        dot_bytes = _colored_dot_bytes(color_map.get(verdict,"#808080"), size=18)
        dot_img = RLImage(dot_bytes, width=12, height=12)
        heading = Paragraph(f"<b>{hk}</b>  <font size=10 color='grey'>({verdict})</font>", styles["Heading2Custom"])
        row = Table([[dot_img, heading]], colWidths=[0.2*inch, 6.0*inch])
        row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("LEFTPADDING",(0,0),(-1,-1),0)]))
        story.append(row)
        story.append(Spacer(1,4))
        story.append(Paragraph(f"<b>Why:</b> {why}", styles["NormalCustom"]))
        story.append(Spacer(1,4))
        if fixes:
            bl = [ListItem(Paragraph(str(x), styles["NormalCustom"]), leftIndent=10) for x in fixes]
            story.append(Paragraph("<b>Suggested fixes:</b>", styles["NormalCustom"]))
            story.append(ListFlowable(bl, bulletType="bullet", start="circle"))
        else:
            story.append(Paragraph("<b>Suggested fixes:</b> None", styles["Small"]))
        story.append(Spacer(1,12))

    story.append(PageBreak())
    story.append(Paragraph("Appendix: Raw JSON", styles["Heading2Custom"]))
    story.append(Spacer(1,6))
    story.append(Paragraph("<pre>"+json.dumps(json_obj, indent=2).replace("<","&lt;").replace(">","&gt;")+"</pre>", styles["Small"]))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return out_pdf_path
