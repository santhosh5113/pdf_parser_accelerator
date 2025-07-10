import fitz  # PyMuPDF
import requests
import os
import base64
import json
from collections import Counter
import pdfplumber
import camelot
import re

PDF_PATH = None  # Will be set in main
PROMPT = (
    "You are an expert in document layout analysis. "
    "Classify ONLY THIS SINGLE PAGE image as one of: "
    "'Native Text', 'Native Table', 'Native Math Heavy', 'Scanned Text', 'Scanned Table', or 'Scanned Math Heavy'. "
    "Definitions: "
    "'Native' = machine-readable/selectable text; 'Scanned' = image-based, non-selectable text. "
    "'Math Heavy' = any presence of equations, mathematical symbols, or scientific notation. "
    "'Table' = clear tabular structure, indicated by gridlines, rows/columns, cell borders, or regularly aligned text. "
    "If a table or math is present, classify accordingly even if mixed with text. "
    "Return ONLY the predicted class label and a one-line justification. "
    "Do NOT mention or invent other pages. "
    "Examples:\n"
    "Native Text – The page contains only machine-readable text.\n"
    "Native Table – The page contains a machine-readable table (gridlines, columns, or cell borders).\n"
    "Native Math Heavy – The page contains equations or scientific notation.\n"
    "Scanned Text – The page is an image with mostly text.\n"
    "Scanned Table – The page is an image with a table (gridlines, columns, or cell borders).\n"
    "Scanned Math Heavy – The page is an image with equations or scientific notation."
)
TEMP_IMAGE_DIR = "temp_images"

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama default

os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def analyze_image_with_ollama(image_path: str, prompt: str, model: str = "llava") -> str:
    with open(image_path, "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [img_b64]
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120, stream=True)
        result = ""
        for line in response.iter_lines():
            if line:
                # Ollama streams JSON lines, each with a 'response' key
                try:
                    data = json.loads(line.decode("utf-8"))
                    result += data.get("response", "")
                except Exception:
                    continue
        return result.lower()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return "other"

def extract_category(response):
    """
    Extracts and normalizes the predicted class label from the model's response.
    Returns one of the six routing categories, or 'other' if not matched.
    """
    categories = [
        "native text",
        "native table",
        "native math heavy",
        "scanned text",
        "scanned table",
        "scanned math heavy"
    ]
    response_lower = response.lower()
    for cat in categories:
        if cat in response_lower:
            return cat
    # Try to match partials (e.g., "math heavy" or "table")
    if "math" in response_lower and "scanned" in response_lower:
        return "scanned_math_heavy"
    if "math" in response_lower and "native" in response_lower:
        return "native_math_heavy"
    if "table" in response_lower and "scanned" in response_lower:
        return "scanned_table"
    if "table" in response_lower and "native" in response_lower:
        return "native_table"
    if "text" in response_lower and "scanned" in response_lower:
        return "scanned_text"
    if "text" in response_lower and "native" in response_lower:
        return "native_text"
    return "other"

def is_native_page(page):
    """Returns True if the page has selectable text."""
    return bool(page.get_text().strip())

def detect_table_with_camelot(pdf_path, page_number):
    """Returns True if Camelot detects a table on the given page (1-indexed)."""
    try:
        tables = camelot.read_pdf(pdf_path, pages=str(page_number+1), flavor='stream')
        return tables.n > 0
    except Exception as e:
        print(f"Camelot error on page {page_number+1}: {e}")
        return False

def detect_equation_in_text(text):
    math_patterns = [
        r'∂', r'∑', r'∫', r'√', r'±', r'≠', r'≤', r'≥', r'd/dt', r'd/dx', r'dy/dx',
        r'\\frac', r'\\sum', r'\\int', r'\\sqrt', r'\\begin\{equation\}', r'\\_', r'\\^',
        r'[A-Za-z0-9]+\s*\^',  # exponents
        r'[A-Za-z0-9]+\s*_',    # subscripts
    ]
    for pattern in math_patterns:
        if re.search(pattern, text):
            return True
    return False

def build_llm_prompt(is_native, camelot_table_found, equation_found):
    detection_lines = []
    detection_lines.append(f"Detection results: This page is classified as {'native' if is_native else 'scanned'} (machine-readable/selectable text: {is_native}).")
    detection_lines.append(f"Camelot table detection: {'table detected' if camelot_table_found else 'no table detected'}.")
    detection_lines.append(f"Equation detection in text: {'equation detected' if equation_found else 'no equation detected'}.")
    detection_lines.append(
        "You MUST use these detection results to inform your classification. "
        "If a table or equation is detected, you should strongly consider classifying as 'Native Table' or 'Native Math Heavy' as appropriate, unless the image clearly contradicts this. "
    )
    detection_block = '\n'.join(detection_lines)
    prompt = (
        f"{detection_block}\n"
        "Given this information and the image, classify the page as one of: "
        "'Native Text', 'Native Table', 'Native Math Heavy', 'Scanned Text', 'Scanned Table', or 'Scanned Math Heavy'. "
        "Definitions: "
        "'Native' = machine-readable/selectable text; 'Scanned' = image-based, non-selectable text. "
        "'Math Heavy' = any presence of equations, mathematical symbols, or scientific notation. "
        "'Table' = clear tabular structure, indicated by gridlines, rows/columns, cell borders, or regularly aligned text. "
        "If a table or math is present, classify accordingly even if mixed with text. "
        "Return ONLY the predicted class label and a one-line justification."
    )
    return prompt

def analyze_pdf_with_ollama(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    page_types = []
    for i, page in enumerate(doc):
        is_native = is_native_page(page)
        camelot_table_found = detect_table_with_camelot(pdf_path, i) if is_native else False
        text = page.get_text() if is_native else ""
        equation_found = detect_equation_in_text(text) if is_native else False

        print(f"Page {i+1} debug info: is_native={is_native}, camelot_table_found={camelot_table_found}, equation_found={equation_found}")

        # Render image for LLM
        pix = page.get_pixmap(dpi=200)
        img_path = os.path.join(TEMP_IMAGE_DIR, f"page_{i+1}.png")
        pix.save(img_path)

        # Build prompt dynamically based on detection results
        llm_prompt = build_llm_prompt(is_native, camelot_table_found, equation_found)

        # Call LLM
        result = analyze_image_with_ollama(img_path, llm_prompt, model="llava:13b")
        label = extract_category(result)
        page_types.append(label)
        print(f"Page {i+1}: {label} (raw: {result})")
    doc.close()
    # Aggregate page types to classify the document
    counts = Counter(page_types)
    most_common_label, count = counts.most_common(1)[0]
    doc_type = most_common_label if count / total_pages > 0.4 else "other"
    print(f"\nOverall document type: {doc_type}")
    return doc_type

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python analyze_pdf2.py <pdf_path>")
        sys.exit(1)
    PDF_PATH = sys.argv[1]
    category = analyze_pdf_with_ollama(PDF_PATH)
    print(category)
