import os
import requests
import argparse
import json

def surya_ocr_api(file_path, endpoint="https://api.datalab.to/v1/ocr"):
    """
    Send a PDF or image to Surya OCR cloud API and return the result.
    """
    api_key = os.environ.get("SURYA_API_KEY")
    if not api_key:
        raise ValueError("SURYA_API_KEY environment variable not set.")
    with open(file_path, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(endpoint, files=files, headers=headers)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Surya OCR Cloud API Integration")
    parser.add_argument("input_file", help="Path to PDF or image file to process")
    parser.add_argument("output_file", nargs="?", help="Output JSON file (optional)")
    args = parser.parse_args()

    result = surya_ocr_api(args.input_file)
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result written to {args.output_file}")
    else:
        print(json.dumps(result, indent=2)) 