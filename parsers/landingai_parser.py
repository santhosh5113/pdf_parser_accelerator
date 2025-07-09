import sys
import json
from agentic_doc.parse import parse_documents

def parse_pdf_with_agentic(pdf_path):
    results = parse_documents([pdf_path])
    parsed_doc = results[0]
    page_map = {}
    for chunk in parsed_doc.chunks:
        for grounding in chunk.grounding:
            page_idx = grounding.page + 1  # 1-based page index
            page_map.setdefault(page_idx, [])
            box = grounding.box
            x1, y1 = box.l, box.t
            w, h = box.r - box.l, box.b - box.t
            page_map[page_idx].append({
                "bboxes": [[x1, y1, w, h]],
                "captions": [chunk.text],
                "chunk_type": chunk.chunk_type,
            })
    return page_map

def main():
    if len(sys.argv) != 3:
        print("Usage: python landingai_parser.py <input_pdf> <output_json>")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    try:
        result = parse_pdf_with_agentic(input_pdf)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Parsed output saved to {output_json}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 