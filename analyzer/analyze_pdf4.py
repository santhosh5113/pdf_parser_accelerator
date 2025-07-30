"""
# OpenAI VLM Dependencies for analyze_pdf4.py
#openai>=1.0.0
#PyMuPDF>=1.23.0
#Pillow>=10.0.0 
OpenAI GPT-4V (Vision) PDF Classification Module

Requirements:
- openai
- fitz (PyMuPDF)
- pillow
- base64
- os

Usage:
    python analyze_pdf4.py <path_to_pdf> [--model gpt-4o] [--save-results]
"""

import sys
import os
import base64
import argparse
import json
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import List, Dict, Any, Optional
from openai import OpenAI
import time

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # Latest OpenAI vision model
TEMP_IMAGE_DIR = "temp_images"
DPI = 300  # High resolution for better VLM analysis

# Classification categories
CATEGORIES = [
    "NATIVE TEXT",
    "NATIVE TABLE", 
    "NATIVE MATH HEAVY",
    "SCANNED TEXT",
    "SCANNED TABLE",
    "SCANNED MATH HEAVY"
]

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 string for OpenAI API."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ Error encoding image {image_path}: {e}")
        return ""

def create_vision_prompt() -> str:
    """Create a comprehensive prompt for GPT-4V PDF classification."""
    return f"""You are an expert document classifier. Analyze this PDF page image and classify it into exactly one of these 6 categories:

CATEGORIES:
1. NATIVE TEXT - Digital PDF with mostly text paragraphs, no tables or heavy math
2. NATIVE TABLE - Digital PDF with tables as main content, structured rows/columns
3. NATIVE MATH HEAVY - Digital PDF with many mathematical equations and formulas
4. SCANNED TEXT - Scanned image of text document, no tables or heavy math
5. SCANNED TABLE - Scanned image where tables are the main content
6. SCANNED MATH HEAVY - Scanned image with significant mathematical content

ANALYSIS GUIDELINES:
- NATIVE vs SCANNED: Look for clean digital text vs. image-based, potentially blurry text
- TABLE: Identify structured data with headers and rows/columns
- MATH HEAVY: Look for equations, mathematical symbols, formulas, variables
- TEXT: Regular paragraphs without table structure or heavy math notation

IMPORTANT RULES:
- Choose the MOST APPROPRIATE single category
- Consider both visual quality (native/scanned) and content type (text/table/math)
- Tables should have clear row/column structure
- Math-heavy documents should contain multiple equations or mathematical notation
- If uncertain, prefer the more specific category (e.g., TABLE over TEXT if table structure is visible)

OVERALL CLASSIFICATION PRIORITY RULES (for multi-page documents):
- If ANY page contains math-heavy content, the overall classification should be MATH HEAVY
- If ANY page contains tables (and no math-heavy content), the overall classification should be TABLE
- MATH HEAVY has higher priority than TABLE - if both are present, classify as MATH HEAVY
- Only classify as TEXT if no pages contain tables or math-heavy content

IMPORTANT: For the overall classification, output ONLY one of these 6 categories:
- NATIVE TEXT
- NATIVE TABLE
- NATIVE MATH HEAVY
- SCANNED TEXT
- SCANNED TABLE
- SCANNED MATH HEAVY

RESPONSE FORMAT:
Return ONLY the exact category name from the list above, nothing else.

Example responses:
NATIVE TABLE
SCANNED MATH HEAVY
NATIVE TEXT
"""

def classify_page_with_openai_vlm(client: OpenAI, image_path: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Classify a single page using OpenAI's Vision Language Model.
    
    Args:
        client: OpenAI client instance
        image_path: Path to the page image
        model: OpenAI model to use (default: gpt-4o)
    
    Returns:
        Dict with classification results
    """
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(image_path)
        if not base64_image:
            return {"error": "Failed to encode image"}
        
        # Create the prompt
        prompt = create_vision_prompt()
        
        # Prepare the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,  # Short response expected
            temperature=0.1  # Low temperature for consistent classification
        )
        
        # Extract the classification
        classification = response.choices[0].message.content.strip().upper()
        
        # Validate classification
        if classification not in CATEGORIES:
            print(f"⚠️ Invalid classification '{classification}', using fallback")
            classification = "NATIVE TEXT"  # Fallback
        
        return {
            "classification": classification,
            "confidence": "high",  # GPT-4V doesn't provide confidence scores
            "model": model,
            "raw_response": response.choices[0].message.content
        }
        
    except Exception as e:
        print(f"❌ Error classifying with OpenAI VLM: {e}")
        return {"error": str(e)}

def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """
    Convert PDF pages to high-resolution images.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of image file paths
    """
    try:
        # Create temp directory
        os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
        
        # Open PDF
        doc = fitz.open(pdf_path)
        image_paths = []
        
        print(f"Converting PDF to images: {pdf_path}")
        print(f"Total pages: {len(doc)}")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Render page at high DPI
            pix = page.get_pixmap(dpi=DPI)
            
            # Save image
            image_path = os.path.join(TEMP_IMAGE_DIR, f"page_{page_num + 1}.png")
            pix.save(image_path)
            image_paths.append(image_path)
            
            print(f"  Page {page_num + 1}: {image_path}")
        
        doc.close()
        return image_paths
        
    except Exception as e:
        print(f"❌ Error converting PDF to images: {e}")
        return []

def classify_pdf_with_openai_vlm(pdf_path: str, model: str = DEFAULT_MODEL, save_results: bool = True) -> Dict[str, Any]:
    """
    Classify PDF pages using OpenAI's Vision Language Model.
    
    Args:
        pdf_path: Path to the PDF file
        model: OpenAI model to use
        save_results: Whether to save results to file
    
    Returns:
        Dict with classification results
    """
    # Validate OpenAI API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return {"error": "Missing OpenAI API key"}
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        return {"error": f"OpenAI client error: {e}"}
    
    # Convert PDF to images
    image_paths = convert_pdf_to_images(pdf_path)
    if not image_paths:
        return {"error": "Failed to convert PDF to images"}
    
    # Classify each page
    results = []
    total_pages = len(image_paths)
    
    print(f"\nClassifying {total_pages} pages with OpenAI {model}...")
    
    for i, image_path in enumerate(image_paths):
        print(f"\nProcessing page {i + 1}/{total_pages}...")
        
        # Add delay to respect rate limits
        if i > 0:
            time.sleep(1)  # 1 second delay between requests
        
        # Classify page
        page_result = classify_page_with_openai_vlm(client, image_path, model)
        
        if "error" in page_result:
            print(f"❌ Error on page {i + 1}: {page_result['error']}")
            results.append({
                "page": i + 1,
                "classification": "ERROR",
                "error": page_result["error"]
            })
        else:
            classification = page_result["classification"]
            print(f"✅ Page {i + 1}: {classification}")
            
            results.append({
                "page": i + 1,
                "classification": classification,
                "confidence": page_result.get("confidence", "high"),
                "model": page_result.get("model", model),
                "raw_response": page_result.get("raw_response", "")
            })
    
    # Determine overall document classification
    successful_classifications = [r["classification"] for r in results if "error" not in r]
    
    if successful_classifications:
        # Count classifications
        from collections import Counter
        classification_counts = Counter(successful_classifications)
        
        # Apply priority rules for overall classification
        has_math_heavy = any("MATH HEAVY" in classification for classification in successful_classifications)
        has_table = any("TABLE" in classification for classification in successful_classifications)
        
        if has_math_heavy:
            # Math heavy has highest priority - find the specific math heavy category
            math_heavy_categories = [c for c in successful_classifications if "MATH HEAVY" in c]
            overall_classification = math_heavy_categories[0]  # Use the first one found
        elif has_table:
            # Table has second priority - find the specific table category
            table_categories = [c for c in successful_classifications if "TABLE" in c]
            overall_classification = table_categories[0]  # Use the first one found
        else:
            # Default to most common classification (likely TEXT)
            most_common = classification_counts.most_common(1)[0]
            overall_classification = most_common[0]
    else:
        overall_classification = "ERROR"
    
    # Prepare final results
    final_results = {
        "pdf_path": pdf_path,
        "model": model,
        "total_pages": total_pages,
        "overall_classification": overall_classification,
        "page_results": results,
        "classification_counts": dict(classification_counts) if successful_classifications else {},
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save results if requested
    if save_results:
        output_path = os.path.splitext(os.path.basename(pdf_path))[0] + "_openai_vlm_results.json"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Results saved to: {output_path}")
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")
    
    # Print summary
    print(f"\n📊 Classification Summary:")
    print(f"   Overall: {overall_classification}")
    print(f"   Total Pages: {total_pages}")
    print(f"   Model: {model}")
    
    if successful_classifications:
        print(f"   Page Classifications:")
        for classification, count in classification_counts.items():
            print(f"     {classification}: {count} pages")
    
    return final_results

def cleanup_temp_images():
    """Clean up temporary image files."""
    try:
        if os.path.exists(TEMP_IMAGE_DIR):
            for file in os.listdir(TEMP_IMAGE_DIR):
                if file.endswith('.png'):
                    os.remove(os.path.join(TEMP_IMAGE_DIR, file))
            print(f"🧹 Cleaned up temporary images in {TEMP_IMAGE_DIR}")
    except Exception as e:
        print(f"⚠️ Could not cleanup temp images: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify PDF pages using OpenAI GPT-4V")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, 
                       choices=["gpt-4o", "gpt-4o-mini", "gpt-4-vision-preview"], 
                       help="OpenAI model to use")
    parser.add_argument("--save-results", action="store_true", 
                       help="Save results to JSON file")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Clean up temporary images after processing")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.isfile(args.pdf_path):
        print(f"❌ File not found: {args.pdf_path}")
        sys.exit(1)
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        # Classify PDF
        results = classify_pdf_with_openai_vlm(
            args.pdf_path, 
            model=args.model, 
            save_results=args.save_results
        )
        
        # Cleanup if requested
        if args.cleanup:
            cleanup_temp_images()
        
        # Exit with error if classification failed
        if "error" in results:
            print(f"❌ Classification failed: {results['error']}")
            sys.exit(1)
        
        print(f"\n✅ Classification completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        cleanup_temp_images()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        cleanup_temp_images()
        sys.exit(1) 