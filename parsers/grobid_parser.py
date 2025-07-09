import sys
import os
import json
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import GrobidParser

def main():
    if len(sys.argv) != 3:
        print("Usage: python grobid_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    # Parse PDF using Grobid
    loader = GenericLoader.from_filesystem(
        os.path.dirname(input_pdf) or ".",
        glob=os.path.basename(input_pdf),
        suffixes=[".pdf"],
        parser=GrobidParser(segment_sentences=False)
    )
    docs = loader.load()

    # Save parsed docs to JSON
    docs_data = [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"docs": docs_data}, f, ensure_ascii=False, indent=2)
    print(f"✅ Parsed output saved to: {output_json}")

if __name__ == "__main__":
    main()
