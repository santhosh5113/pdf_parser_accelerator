# parsers/pdfminer_parser.py

import sys
import json
from pdfminer.high_level import extract_text

def main():
    if len(sys.argv) != 3:
        print("Usage: python pdfminer_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    try:
        text = extract_text(input_pdf)
    except Exception as e:
        print(f"Error extracting text: {e}")
        sys.exit(1)

    output = {"text": text}

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
