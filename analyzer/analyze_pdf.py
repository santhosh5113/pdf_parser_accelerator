# analyze/analyze_pdf.py

import fitz  # PyMuPDF
import re
import os
import tempfile
import subprocess
import json
import pytesseract
from PIL import Image
import io

# Math detection regex patterns
MATH_PATTERNS = [
        r'\\begin\{equation\}', r'\\\[.*?\\\]', r'\\\(.+?\\\)', r'\\frac', r'\\sum', r'\\int', r'\\sqrt',
        r'\\alpha', r'\\beta', r'\\gamma', r'\\pi', r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\exp',
        r'\\leq', r'\\geq', r'\\neq', r'\\approx', r'\\cdot', r'\\times', r'\\pm', r'\\infty', r'\\partial',
        r'\\mathrm', r'\\mathbf', r'\\mathbb', r'\\mathcal', r'\\left', r'\\right', r'\\over', r'\\underline',
    r'\\overline', r'\\dots', r'\\ldots', r'\\cdots', r'\\vdots', r'\\ddots', r'\\forall', r'\\exists',
    r'\$[^$]+\$',
    r'[=+\-*/<>≤≥≪¼½π]'
]

# Helper: Count math patterns in text
def count_math(text):
    count = 0
    for pattern in MATH_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)
    return count

def is_scanned_pdf_tesseract(pdf_path, text_threshold=30, ocr_threshold=30, scanned_ratio=0.5):
    doc = fitz.open(pdf_path)
    scanned_pages = 0
    total_pages = len(doc)
    for page in doc:
        text = page.get_text().strip()
        if len(text) >= text_threshold:
            continue  # Native text found
        # Render page to image
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes()))
        ocr_text = pytesseract.image_to_string(img)
        if len(ocr_text.strip()) >= ocr_threshold:
            scanned_pages += 1
    doc.close()
    ratio = scanned_pages / total_pages if total_pages > 0 else 0
    return ratio > scanned_ratio

def analyze_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        has_text = False
        has_images = False
        has_tables = False
        table_like = False
        math_count = 0
        math_threshold = 10  # You can tune this
        # Try to import advanced table detectors
        try:
            import camelot
        except ImportError:
            camelot = None
        try:
            import pdfplumber
        except ImportError:
            pdfplumber = None
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            images = page.get_images()
            if text and len(text) > 30:  # Only count as text if it's meaningful
                has_text = True
            if images:
                has_images = True
            # PyMuPDF table detection
            try:
                tables = page.find_tables()
                if tables is not None and tables.tables:
                    has_tables = True
            except Exception:
                pass
            # Heuristic for table-like text
            lines = text.splitlines()
            table_lines = [line for line in lines if ('|' in line or '\t' in line)]
            if len(table_lines) > 3:
                table_like = True
            # Math detection in native text
            math_count += count_math(text)
        doc.close()
        # Camelot table detection (on all pages)
        if camelot is not None:
            try:
                tables = camelot.read_pdf(pdf_path, pages="all")
                if tables and tables.n > 0:
                    has_tables = True
            except Exception:
                pass
        # pdfplumber table detection (on all pages)
        if pdfplumber is not None:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        extracted_tables = page.extract_tables()
                        if extracted_tables and len(extracted_tables) > 0:
                            has_tables = True
            except Exception:
                pass
        # Tesseract-based scanned PDF detection
        if is_scanned_pdf_tesseract(pdf_path):
            # Call Donut/OCR for math detection in scanned PDF
            result = subprocess.run([
                "conda", "run", "-n", "donut_env", "python", "parsers/donut_math_detect.py", pdf_path
            ], capture_output=True, text=True)
            try:
                output = json.loads(result.stdout)
                math_count = output.get("math_count", 0)
            except Exception as e:
                print("Donut OCR error:", result.stdout, result.stderr)
                math_count = 0
            if math_count > math_threshold:
                return "scanned_math_heavy"
            else:
                return "scanned_pdf"
        # Prefer native_math_heavy if both are present
        if (has_tables or table_like) and math_count > math_threshold:
            return "native_math_heavy"
        if has_tables or table_like:
            return "native_table"
        if math_count > math_threshold:
            return "native_math_heavy"
        if has_text:
            return "native_text"
            return "unknown"
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return "unknown"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m analyzer.analyze_pdf <pdf_path>")
        sys.exit(1)
    category = analyze_pdf(sys.argv[1])
    print(category)
