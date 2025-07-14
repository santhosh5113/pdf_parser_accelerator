import fitz  # PyMuPDF
import os
import re
from collections import Counter
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

# Initialize Donut model and processor
MODEL_NAME = "naver-clova-ix/donut-base-finetuned-docvqa"
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = DonutProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME).to(device)

PDF_PATH = None  # Will be set in main
TEMP_IMAGE_DIR = "temp_images"
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

# Math detection regex patterns
MATH_PATTERNS = [
    r'∂', r'∑', r'∫', r'√', r'±', r'≠', r'≤', r'≥', r'd/dt', r'd/dx', r'dy/dx',
    r'\\frac', r'\\sum', r'\\int', r'\\sqrt', r'\\begin\{equation\}', r'\\_', r'\\^',
    r'[A-Za-z0-9]+\s*\^',  # exponents
    r'[A-Za-z0-9]+\s*_',    # subscripts
]

def detect_math(text):
    for pattern in MATH_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def donut_ocr(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
    task_prompt = "<s_docvqa><s_question>What is written on the page?<s_answer>"
    outputs = model.generate(pixel_values, max_length=512, num_beams=1)
    result = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    return result

def analyze_pdf_with_donut(pdf_path: str):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    page_summaries = []
    for i, page in enumerate(doc):
        # Render page to image
        pix = page.get_pixmap(dpi=200)
        img_path = os.path.join(TEMP_IMAGE_DIR, f"page_{i+1}.png")
        pix.save(img_path)

        # Use Donut for OCR
        donut_text = donut_ocr(img_path)
        has_text = bool(donut_text.strip())
        is_native = bool(page.get_text().strip())
        # Table detection: simple heuristic (look for table-like words or structure)
        has_table = any(word in donut_text.lower() for word in ["table", "row", "column", "cell"]) or ("|" in donut_text or "," in donut_text)
        has_math = detect_math(donut_text)

        summary = {
            "page": i+1,
            "is_native": is_native,
            "is_scanned": not is_native,
            "has_text": has_text,
            "has_table": has_table,
            "has_math": has_math,
            "ocr_text_sample": donut_text[:100]
        }
        print(f"Page {i+1} summary: {summary}")
        page_summaries.append(summary)
    doc.close()
    # Aggregate document-level summary
    doc_summary = {
        "total_pages": total_pages,
        "native_pages": sum(1 for s in page_summaries if s["is_native"]),
        "scanned_pages": sum(1 for s in page_summaries if s["is_scanned"]),
        "pages_with_text": sum(1 for s in page_summaries if s["has_text"]),
        "pages_with_table": sum(1 for s in page_summaries if s["has_table"]),
        "pages_with_math": sum(1 for s in page_summaries if s["has_math"]),
    }
    print(f"\nDocument summary: {doc_summary}")
    return page_summaries, doc_summary

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyze_pdf3.py <pdf_path>")
        sys.exit(1)
    PDF_PATH = sys.argv[1]
    analyze_pdf_with_donut(PDF_PATH) 