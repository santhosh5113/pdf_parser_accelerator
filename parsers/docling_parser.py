# parsers/docling_parser.py

import sys
import json
import os
import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

def extract_images_from_pdf(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(page_num)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = os.path.join(output_dir, f"page{page_num+1}_img{img_index+1}.{image_ext}")
            with open(image_filename, "wb") as f:
                f.write(image_bytes)
            count += 1
            print(f"🖼️ Saved: {image_filename}")

    if count == 0:
        print("⚠️ No images found.")
    else:
        print(f"✅ {count} images extracted.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python docling_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    output_md = output_json.replace(".json", ".md")
    image_output_dir = output_json.replace(".json", "_images")

    print(f"🔍 Reading PDF: {input_pdf}")
    print(f"📄 Saving JSON to: {output_json}")
    print(f"📝 Saving Markdown to: {output_md}")
    print(f"🖼️ Extracting images to: {image_output_dir}")

    # 1. Run Docling conversion
    try:
        pipeline_options = PdfPipelineOptions(images_scale=4.17)
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(input_pdf)
        print("✅ Docling conversion completed.")
    except Exception as e:
        print(f"❌ Error running Docling: {e}")
        sys.exit(1)

    # 2. Export to JSON
    try:
        json_data = result.document.export_to_dict()
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print("✅ JSON saved successfully.")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")

    # 3. Export to Markdown
    '''try:
        markdown_text = result.document.export_to_markdown()
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print("✅ Markdown saved successfully.")
    except Exception as e:
        print(f"⚠️ Skipped Markdown export: {e}")'''

    # 4. Extract images
    try:
        extract_images_from_pdf(input_pdf, image_output_dir)
    except Exception as e:
        print(f"❌ Image extraction failed: {e}")

if __name__ == "__main__":
    main()
