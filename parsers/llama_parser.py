# parsers/llamaparse_parser.py
'''
import os
import sys
import json
from llama_cloud_services import LlamaParse

def main():
    if len(sys.argv) != 3:
        print("Usage: python parsers/llamaparse_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    print(f"📥 Parsing PDF with LlamaParse: {input_pdf}")
    print(f"📤 Output will be saved to: {output_json}")

    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("❌ Error: LLAMA_CLOUD_API_KEY is not set in environment variables.")
        sys.exit(1)

    try:
        parser = LlamaParse(
            api_key=api_key,
            premium_mode=True,
            num_workers=2,
            verbose=True,
            language="en",
        )

        result = parser.parse(input_pdf)

        full_result = []
        for page in result.pages:
           full_result.append({
    "text": page.text,
    "markdown": page.md,
    "images": [img.__dict__ for img in getattr(page, "images", [])],
    "layout": getattr(page, "layout", None)
})

        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump({"pages": full_result}, f, indent=2, ensure_ascii=False)

        print("✅ LlamaParse JSON saved successfully!")

    except Exception as e:
        print(f"❌ Error while parsing with LlamaParse: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()'''

import os
import sys
from llama_cloud_services import LlamaParse

def main():
    if len(sys.argv) != 3:
        print("Usage: python parsers/llamaparse_parser.py <input_pdf_path> <output_md_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_md = sys.argv[2]

    print(f"📥 Parsing PDF with LlamaParse: {input_pdf}")
    print(f"📤 Output will be saved to: {output_md}")

    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("❌ Error: LLAMA_CLOUD_API_KEY is not set in environment variables.")
        sys.exit(1)

    try:
        parser = LlamaParse(
            api_key=api_key,
            premium_mode=True,
            num_workers=2,
            verbose=True,
            language="en",
        )

        result = parser.parse(input_pdf)

        # Concatenate all markdown content from each page
        all_md = "\n\n".join(page.md for page in result.pages if page.md)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_md), exist_ok=True)

        # Save markdown text to output file
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(all_md)

        print("✅ LlamaParse markdown saved successfully!")

    except Exception as e:
        print(f"❌ Error while parsing with LlamaParse: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
