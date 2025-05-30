# parsers/vision_parser.py

import sys
import json
from vision_parse import VisionParser

def main(pdf_path, output_path):
    print(f"📥 Processing: {pdf_path}")
    print(f"📤 Output will be saved to: {output_path}")

    try:
        parser = VisionParser(
            model_name="llava:13b",  # Ollama model, make sure it's pulled and Ollama daemon is running
            temperature=0,
            custom_prompt="- Only use data found directly in the input. Do not add or invent details. If data is missing, leave it as null or \"Not Available\".Do not assume or correct data format unless it's clearly stated.",
            image_mode="url",
            detailed_extraction=True,
            enable_concurrency=False,
        )

        markdown_pages = parser.convert_pdf(pdf_path)

        with open(output_path, "w") as f:
            json.dump({"pages": markdown_pages}, f, indent=2)

        print("✅ PDF processed successfully!")

    except Exception as e:
        print(f"❌ Error during VisionParser execution: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/vision_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    main(input_pdf, output_json)
