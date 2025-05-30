# database/run_pipeline.py

import sys
import subprocess
import os
from analyzer.analyze_pdf import analyze_pdf  # ✅ updated import
from database.vector_store import store_pdf_chunks


def run_parser(env_name, script, input_pdf, output_json):
    subprocess.run([
        "conda", "run", "-n", env_name, "python",
        f"parsers/{script}", input_pdf, output_json
    ])

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_pipeline.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    category = analyze_pdf(input_pdf)
    print(f"📊 Detected category: {category}")

    # Route all scanned PDFs to llama_parse_env
    if category == "scanned_pdf":
        run_parser("llama_parse_env", "llama_parser.py", input_pdf, output_json)
    elif category == "native_table":
        run_parser("docling_env", "docling_parser.py", input_pdf, output_json)
    elif category == "native_text":
        run_parser("pdfminer_env", "pdfminer_parser.py", input_pdf, output_json)
    else:
        print("❌ Unable to determine suitable parser for this PDF.")
        return

    # Store output in vector DB
    store_pdf_chunks(output_json, os.path.basename(input_pdf))


if __name__ == "__main__":
    main()
 