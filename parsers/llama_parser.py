import os
import sys
import json
from llama_cloud_services import LlamaParse

def serialize_page_content(content):
    """Helper function to ensure content is JSON serializable."""
    if content is None:
        return None
    
    if isinstance(content, (str, int, float, bool)):
        return content
    
    if isinstance(content, (list, tuple)):
        return [serialize_page_content(item) for item in content]
    
    if isinstance(content, dict):
        return {k: serialize_page_content(v) for k, v in content.items()}
    
    # Convert any other type to string representation
    return str(content)

def main():
    if len(sys.argv) != 3:
        print("Usage: python parsers/llama_parser.py <input_pdf_path> <output_json_path>")
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
            structured_output=True  # Enable JSON output
        )

        # Parse the PDF using the recommended method
        extra_info = {"file_name": input_pdf}
        with open(input_pdf, "rb") as f:
            result = parser.load_data(f, extra_info=extra_info)

        # Extract structured data from each page
        output_data = []
        for page in result:
            page_data = {
                "page_number": getattr(page, "pageNumber", None),
                "content": getattr(page, "structuredData", None) if hasattr(page, "structuredData") else getattr(page, "text", None),
            }
            output_data.append(page_data)

        # Save to JSON file
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully parsed PDF and saved JSON to: {output_json}")

    except Exception as e:
        print(f"❌ Error parsing PDF: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

