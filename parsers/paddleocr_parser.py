import sys
import os
import json
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import camelot

# Initialize OCR model
ocr = PaddleOCR(use_textline_orientation=True, lang='en', ocr_version='PP-OCRv4')

def is_native_pdf_page(page):
    # Returns True if the page contains extractable text
    text = page.get_text().strip()
    return bool(text)

def extract_text_native(page):
    return page.get_text()

def extract_tables_native(pdf_path, page_num):
    # Camelot uses 1-based page numbers
    try:
        tables = camelot.read_pdf(pdf_path, pages=str(page_num+1), flavor='lattice')
        if len(tables) == 0:
            tables = camelot.read_pdf(pdf_path, pages=str(page_num+1), flavor='stream')
        return [table.df.values.tolist() for table in tables]
    except Exception as e:
        print(f"❌ Camelot error on page {page_num+1}: {e}")
        return []

def convert_pdf_to_images(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
        print(f"✅ Saved image: {image_path}")
    
    return image_paths

def run_ocr_on_image(image_path):
    result = ocr.ocr(image_path)
    lines = []
    if result and isinstance(result, list):
        for line in result:
            if len(line) == 2:
                box, (text, score) = line
            elif len(line) == 3:
                box, (text, score), _ = line
            else:
                continue
            lines.append(text)
    return '\n'.join(lines)

def main(pdf_path, output_json_path):
    print(f"📄 Starting hybrid extraction on: {pdf_path}")
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    image_dir = os.path.join("temp_images", os.path.splitext(os.path.basename(pdf_path))[0])
    os.makedirs(image_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    text_results = []
    table_results = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        if is_native_pdf_page(page):
            # Native PDF: extract text and tables
            text = extract_text_native(page)
            tables = extract_tables_native(pdf_path, page_num)
            print(f"✅ Page {page_num+1}: Native PDF (text+tables)")
        else:
            # Scanned PDF: convert to image, use OCR
            image_path = os.path.join(image_dir, f"page_{page_num + 1}.png")
            if not os.path.exists(image_path):
                pix = page.get_pixmap(dpi=300)
                pix.save(image_path)
            text = run_ocr_on_image(image_path)
            tables = []  # Placeholder: integrate PaddleOCR table pipeline here if needed
            print(f"✅ Page {page_num+1}: Scanned PDF (OCR)")
        text_results.append(text)
        table_results.append(tables)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump({"text": text_results, "tables": table_results}, f, indent=2, ensure_ascii=False)
    print(f"✅ Hybrid extraction output saved to: {output_json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/paddleocr_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    main(input_pdf, output_json)