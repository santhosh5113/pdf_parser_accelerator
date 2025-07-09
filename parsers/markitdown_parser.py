# parsers/markitdown_parser.py

import sys
import os
import json
from markitdown import MarkItDown
import re

# Add Camelot import
import camelot

def extract_tables_with_camelot(pdf_path):
    # Try both flavors for robustness
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    if len(tables) == 0:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    extracted_tables = []
    for table in tables:
        extracted_tables.append(table.df.values.tolist())  # as 2D array
    return extracted_tables

def main(input_path, output_path):
    print(f"📥 Extracting text with MarkItDown and tables with Camelot: {input_path}")
    print(f"📤 Output will be saved to: {output_path}")

    try:
        # Extract text with MarkItDown
        md = MarkItDown()
        result = md.convert(input_path)
        markdown_text = result.text_content

        # Extract tables with Camelot
        tables = extract_tables_with_camelot(input_path)

        # Ensure output folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save structured JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"text": markdown_text, "tables": tables}, f, indent=2, ensure_ascii=False)

        print("✅ Text and table extraction completed successfully.")

    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/markitdown_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)
