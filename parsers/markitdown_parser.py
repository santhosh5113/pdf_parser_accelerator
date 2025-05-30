# parsers/markitdown_parser.py

import sys
import os
import json
from markitdown import MarkItDown

def main(input_path, output_path):
    print(f"📥 Converting spreadsheet to Markdown: {input_path}")
    print(f"📤 Output will be saved to: {output_path}")

    try:
        md = MarkItDown()
        result = md.convert(input_path)

        # Ensure output folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save as Markdown in a JSON structure
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"markdown": result.text_content}, f, indent=2, ensure_ascii=False)

        print("✅ Markdown conversion completed successfully.")

    except Exception as e:
        print(f"❌ Error during MarkItDown conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/markitdown_parser.py <input_xlsx_path> <output_json_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
