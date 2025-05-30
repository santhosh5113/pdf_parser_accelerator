# analyze/analyze_pdf.py

import fitz  # PyMuPDF
import re

#defining a function to analyse the pdf.
def analyze_pdf(file_path):
    doc = fitz.open(file_path)
    has_images = False
    has_text = False
    table_detected = False
    all_text = ""

    table_keywords = ['table', 'row', 'column', 'cell', 'data', 'header']

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            has_text = True
            all_text += text + "\n"

            if any(word in text.lower() for word in table_keywords):
                table_detected = True

        if page.get_images():
            has_images = True

    if has_text:
        if table_detected or len(all_text.splitlines()) > 50:
            return "native_table"
        else:
            return "native_text"
    elif has_images:
        return "scanned_pdf"  # ✅ one unified scanned category

    return "unknown"
