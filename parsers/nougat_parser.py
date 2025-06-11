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

    def process_page(self, image: Image.Image, page_idx: int, max_retries: int = 5) -> Tuple[str, bool]:
        """
        Process a single page with retries and error handling.
        
        Args:
            image (Image.Image): PIL Image of the page
            page_idx (int): Page number (1-based)
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            Tuple[str, bool]: (Extracted text, Has equations)
        """
        retry_count = 0
        last_error = None
        best_text = ""
        has_equations = False
        
        while retry_count < max_retries:
            try:
                # Generate text from the image using default parameters
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
                current_has_equations = self.has_equations(text)
                
                # Keep the best result (prioritize text with equations)
                if not best_text or (current_has_equations and not has_equations) or len(text) > len(best_text):
                    best_text = text
                    has_equations = current_has_equations
                
                # If we have equations and good content, we can stop
                if has_equations and len(best_text.strip()) > 100:
                    break
                
                # If text is empty, always retry
                if not text.strip():
                    raise ValueError("Empty text output")
                
                # If no equations found but we expect them (based on previous success),
                # and we haven't maxed out retries, try again
                if not current_has_equations and retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(2)  # Longer wait between retries
                    continue
                
                return best_text.strip(), has_equations
                
            except Exception as e:
                last_error = e
                retry_count += 1
                logger.warning(f"Retry {retry_count}/{max_retries} for page {page_idx} due to: {str(e)}")
                time.sleep(2)  # Longer wait between retries
        
        if not best_text.strip():
            logger.error(f"Failed to process page {page_idx} after {max_retries} attempts: {str(last_error)}")
            return "", False
            
        return best_text.strip(), has_equations

    def parse_pdf(self, pdf_path: str, output_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract its content including equations.
        
        Args:
            pdf_path (str): Path to the input PDF file
            output_path (str): Path where to save the output JSON
            
        Returns:
            Dict[str, Any]: Dictionary containing the parsed content
        """
        try:
            # Load and process the PDF
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images
            images = rasterize_paper(pdf_path)
            if not images:
                raise ValueError("No images found in PDF")
            
            # Process each page
            pages = []
            failed_pages = []
            total_equations = 0
            
            for page_idx, image_bytes in enumerate(images, 1):
                logger.info(f"Processing page {page_idx}")
                
                try:
                    # Convert BytesIO to PIL Image
                    if isinstance(image_bytes, io.BytesIO):
                        image_bytes.seek(0)
                        image = Image.open(image_bytes).convert('RGB')
                    else:
                        image = image_bytes
                    
                    # Process the page with retries
                    text, has_equations = self.process_page(image, page_idx)
                    
                    # Update equation count
                    if has_equations:
                        total_equations += 1
                    
                    # Store page content
                    pages.append({
                        "page_number": page_idx,
                        "content": text,
                        "has_equations": has_equations,
                        "status": "success" if text else "failed"
                    })
                    
                    if not text:
                        failed_pages.append(page_idx)
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_idx}: {str(e)}")
                    pages.append({
                        "page_number": page_idx,
                        "content": "",
                        "has_equations": False,
                        "status": "error",
                        "error": str(e)
                    })
                    failed_pages.append(page_idx)
            
            # Prepare output
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
                # Add full text for easy access, excluding failed pages
                "full_text": "\n\n".join(page["content"] for page in pages if page["content"])
            }
            
            # Save to JSON
            logger.info(f"Saving output to {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Log summary
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
