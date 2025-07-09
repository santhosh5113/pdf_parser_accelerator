import pdfplumber
import json
import argparse
import os

def extract_pdf_metadata(pdf):
    return pdf.metadata

def extract_text_by_page(pdf):
    return {i: page.extract_text() or "" for i, page in enumerate(pdf.pages)}

def extract_tables_by_page(pdf):
    tables = {}
    for i, page in enumerate(pdf.pages):
        page_tables = page.extract_tables()
        # Each table is a list of rows, each row is a list of cells
        tables[i] = page_tables
    return tables

def extract_images_by_page(pdf, output_dir=None):
    # pdfplumber exposes images as dicts with x0, y0, x1, y1, width, height, and stream
    images = {}
    for i, page in enumerate(pdf.pages):
        page_images = []
        for img in page.images:
            img_dict = {k: img[k] for k in img if k != "stream"}
            if output_dir:
                # Save image as file
                img_obj = page.to_image(resolution=150)
                bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                img_path = os.path.join(output_dir, f"page_{i+1}_img_{len(page_images)+1}.png")
                img_obj.crop(bbox).save(img_path, format="PNG")
                img_dict["file"] = img_path
            page_images.append(img_dict)
        images[i] = page_images
    return images

def parse_pdf(input_path, output_path, extract_images=False):
    with pdfplumber.open(input_path) as pdf:
        result = {
            "metadata": extract_pdf_metadata(pdf),
            "text_by_page": extract_text_by_page(pdf),
            "tables_by_page": extract_tables_by_page(pdf),
        }
        if extract_images:
            images_dir = os.path.join(os.path.dirname(output_path), "images")
            os.makedirs(images_dir, exist_ok=True)
            result["images_by_page"] = extract_images_by_page(pdf, images_dir)
        # Save to JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"PDF parsed. Results saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Parse PDF with pdfplumber (text, tables, metadata, images)")
    parser.add_argument("input_path", help="Path to input PDF")
    parser.add_argument("output_path", help="Path to output JSON")
    parser.add_argument("--images", action="store_true", help="Extract images and save to disk")
    args = parser.parse_args()
    parse_pdf(args.input_path, args.output_path, extract_images=args.images)

if __name__ == "__main__":
    main()
