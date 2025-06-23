import sys
import os
import json
import fitz  # PyMuPDF
from paddleocr import PaddleOCR

# Initialize OCR model
ocr = PaddleOCR(use_textline_orientation=True, lang='en', ocr_version='PP-OCRv4')

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

def run_ocr_on_images(image_paths):
    all_results = []

    for i, image_path in enumerate(image_paths):
        print(f"🔍 Running OCR on: {image_path}")
        try:
            result = ocr.predict(image_path)
            page_results = []

            if result and isinstance(result, list):
                for line in result:
                    if len(line) == 2:
                        box, (text, score) = line
                    elif len(line) == 3:
                        box, (text, score), _ = line  # Sometimes extra info is present
                    else:
                        continue
                    page_results.append({
                        "box": box,
                        "text": text,
                        "score": score
                    })

            all_results.append({
                "page": i + 1,
                "results": page_results
            })

        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")

    return all_results

def main(pdf_path, output_json_path):
    print(f"📄 Starting PaddleOCR on: {pdf_path}")
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    image_dir = os.path.join("temp_images", os.path.splitext(os.path.basename(pdf_path))[0])

    image_paths = convert_pdf_to_images(pdf_path, image_dir)
    results = run_ocr_on_images(image_paths)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OCR output saved to: {output_json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/paddleocr_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    main(input_pdf, output_json)