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

TEMP_IMAGE_DIR = "temp_images"

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama default

os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

def analyze_image_with_ollama(image_path: str, prompt: str, model: str = "llava") -> str:
    # Add example images for few-shot prompting
    example_table_path = os.path.join(TEMP_IMAGE_DIR, "example_table.png")
    example_math_path = os.path.join(TEMP_IMAGE_DIR, "example_math.png")
    images_b64 = []
    # Encode example images if they exist
    for ex_path in [example_table_path, example_math_path]:
        if os.path.exists(ex_path):
            with open(ex_path, "rb") as img_file:
                images_b64.append(base64.b64encode(img_file.read()).decode("utf-8"))
    # Encode the actual page image
    with open(image_path, "rb") as img_file:
        images_b64.append(base64.b64encode(img_file.read()).decode("utf-8"))
    payload = {
        "model": model,
        "prompt": prompt,
        "images": images_b64
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120, stream=True)
        result = ""
        for line in response.iter_lines():
            if line:
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
    
    prompt = """
    You are a document classification expert.

    You will receive a PDF page as an image and classify it strictly into one of the following six categories:

    - Native Text
    - Native Table
    - Native Math Heavy
    - Scanned Text
    - Scanned Table
    - Scanned Math Heavy

    ---

    Step 1: Determine format:
    - Native: Clean, digital, selectable
    - Scanned: Image-based, low-res or photo

    Step 2: Determine content type:
    - Table: Visibly structured rows/columns (headers + data)
    - Math Heavy: Equations, variables, math symbols
    - Text: Paragraphs with no table layout or formulas

    ❗ RULE: Even if the page contains numbers, only classify it as a Table or Math-heavy if the layout clearly shows table structure or math notation.

    ---

    ⚠️ REQUIRED: Always return a classification, never leave it blank.

    Output:
    ---
    Page Classification: <exact one of the 6 categories>
    Reason: <1–2 sentence explanation using visual structure and content>
    ---
    """


   
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
        result = analyze_image_with_ollama(img_path, llm_prompt, model="gemma3:12b-it-qat")
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
