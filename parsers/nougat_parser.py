import sys
import json
import logging
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import torch
from PIL import Image
from nougat import NougatModel
from nougat.postprocessing import markdown_compatible
from nougat.dataset.rasterize import rasterize_paper
import io
import pytesseract
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NougatParser:
    def __init__(self, model_name: str = "facebook/nougat-base"):
        """Initialize the Nougat parser."""
        try:
            logger.info(f"Loading Nougat model {model_name}...")
            self.model = NougatModel.from_pretrained(model_name)
            
            # Move model to GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Model loaded successfully and moved to {self.device}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def has_equations(self, text: str) -> bool:
        """
        Check if text contains LaTeX equations.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text contains equations
        """
        # Common LaTeX equation markers
        equation_patterns = [
            r'\\\[.*?\\\]',  # Display math mode
            r'\\\(.*?\\\)',  # Inline math mode
            r'\$\$.*?\$\$',  # Double dollar display math
            r'\$.*?\$',      # Single dollar inline math
            r'\\begin\{equation\}.*?\\end\{equation\}',
            r'\\begin\{align\*?\}.*?\\end\{align\*?\}',
            r'\\begin\{eqnarray\*?\}.*?\\end\{eqnarray\*?\}'
        ]
        
        for pattern in equation_patterns:
            if re.search(pattern, text, re.DOTALL):
                return True
        return False

    def process_page(self, image: Image.Image, page_idx: int) -> Tuple[str, bool, bool]:
        """
        Process a single page with error handling and Tesseract fallback.
        Returns (Extracted text, Has equations, Used Tesseract fallback)
        """
        try:
            # Generate text from the image using Nougat
            output = self.model.inference(image=image)
            # Clean and extract text from output
            if isinstance(output, dict):
                if 'predictions' in output and isinstance(output['predictions'], list):
                    text = ' '.join(pred for pred in output['predictions'] if pred)
                elif 'text' in output:
                    text = output['text']
                else:
                    text = str(output)
            else:
                text = str(output)
            # Post-process the output
            text = markdown_compatible(text)
            # Check for equations
            has_equations = self.has_equations(text)
            if not text.strip():
                raise ValueError("Empty text output from Nougat")
            return text.strip(), has_equations, False
        except Exception as e:
            logger.warning(f"Nougat failed for page {page_idx} ({e}), using Tesseract fallback.")
            # Fallback to Tesseract OCR
            try:
                text = pytesseract.image_to_string(image)
                has_equations = self.has_equations(text)
                return text.strip(), has_equations, True
            except Exception as e2:
                logger.error(f"Tesseract also failed for page {page_idx}: {e2}")
                return "", False, True

    def parse_pdf(self, pdf_path: str, output_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            logger.info(f"Calling rasterize_paper on: {pdf_path}")
            images = rasterize_paper(pdf_path)
            logger.info(f"rasterize_paper returned {len(images)} images")
            if not images:
                raise ValueError("No images found in PDF")
            pages = []
            failed_pages = []
            total_equations = 0
            full_texts = []
            # Prepare directory for failed images
            failed_img_dir = os.path.join(os.path.dirname(output_path), 'failed_pages_images')
            os.makedirs(failed_img_dir, exist_ok=True)
            for page_idx, image_bytes in enumerate(images, 1):
                logger.info(f"Processing page {page_idx}")
                try:
                    if isinstance(image_bytes, io.BytesIO):
                        image_bytes.seek(0)
                        image = Image.open(image_bytes).convert('RGB')
                    else:
                        image = image_bytes
                    text, has_equations, used_tesseract = self.process_page(image, page_idx)
                    if has_equations:
                        total_equations += 1
                    pages.append({
                        "page_number": page_idx,
                        "content": text,
                        "has_equations": has_equations,
                        "status": "success" if text else "failed",
                        "used_tesseract": used_tesseract
                    })
                    full_texts.append(text)
                    if not text:
                        failed_pages.append(page_idx)
                        # Save failed image for debugging
                        fail_img_path = os.path.join(failed_img_dir, f"page_{page_idx}.png")
                        image.save(fail_img_path)
                except Exception as e:
                    logger.error(f"Error processing page {page_idx}: {str(e)}")
                    pages.append({
                        "page_number": page_idx,
                        "content": "",
                        "has_equations": False,
                        "status": "error",
                        "error": str(e),
                        "used_tesseract": False
                    })
                    failed_pages.append(page_idx)
                    # Save failed image for debugging
                    try:
                        fail_img_path = os.path.join(failed_img_dir, f"page_{page_idx}.png")
                        image.save(fail_img_path)
                    except Exception:
                        pass
            result = {
                "metadata": {
                    "source_file": pdf_path,
                    "model": "facebook/nougat-base",
                    "num_pages": len(images),
                    "successful_pages": len(images) - len(failed_pages),
                    "failed_pages": failed_pages,
                    "total_equations": total_equations,
                    "processing_date": logging.Formatter().converter()
                },
                "pages": pages,
                # Add full text for easy access, including all pages
                "full_text": "\n\n".join(full_texts)
            }
            logger.info(f"Saving output to {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Processing complete: {result['metadata']['successful_pages']}/{result['metadata']['num_pages']} pages successful")
            logger.info(f"Found equations on {total_equations} pages")
            if failed_pages:
                logger.warning(f"Failed pages: {failed_pages}")
            return result
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

def main():
    if len(sys.argv) != 3:
        print("Usage: python nougat_parser.py <input_pdf> <output_json>")
        sys.exit(1)
        
    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    
    parser = NougatParser()
    parser.parse_pdf(input_pdf, output_json)

if __name__ == "__main__":
    main()
