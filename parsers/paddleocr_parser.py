import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, use_gpu: bool = False):
        """Initialize the PDF Parser with PaddleOCR.
        
        Args:
            use_gpu: Whether to use GPU for OCR processing
        """
        self.ocr = PaddleOCR(
            use_textline_orientation=True,  # This handles text orientation
            lang='en',
            ocr_version='PP-OCRv4',
            use_gpu=use_gpu,  # Use GPU if available
            cpu_threads=os.cpu_count()  # Use all available CPU cores for parallel processing
        )
        self.temp_dir = Path('temp_images')

    def _create_temp_dir(self) -> None:
        """Create temporary directory for storing images."""
        self.temp_dir.mkdir(exist_ok=True)

    def _cleanup_temp_dir(self) -> None:
        """Clean up temporary directory and its contents."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary files")

    def convert_pdf_to_images(self, pdf_path: str) -> List[Path]:
        """Convert PDF pages to images.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of paths to the generated images
        """
        image_paths = []
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)  # Higher DPI for better quality
                image_path = self.temp_dir / f"page_{page_num + 1}.png"
                pix.save(str(image_path))
                image_paths.append(image_path)
                logger.info(f"Converted page {page_num + 1}/{total_pages} to image")
            
            doc.close()
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise

    def process_image(self, image_path: Path, page_num: int) -> Dict[str, Any]:
        """Process a single image with OCR.
        
        Args:
            image_path: Path to the image file
            page_num: Page number for the image
            
        Returns:
            Dictionary containing OCR results for the page
        """
        try:
            result = self.ocr.ocr(str(image_path), cls=True)
            
            if not result or not result[0]:
                logger.warning(f"No text detected on page {page_num}")
                return {"page": page_num, "results": []}
            
            page_results = []
            for line in result[0]:
                box = line[0]
                text, confidence = line[1]
                
                # Filter out low confidence results
                if confidence < 0.5:
                    continue
                    
                page_results.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bounding_box": box
                })
            
            return {
                "page": page_num,
                "results": page_results
            }
            
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {str(e)}")
            return {
                "page": page_num,
                "error": str(e),
                "results": []
            }

    def parse_pdf(self, pdf_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Parse a PDF file and extract text using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            output_path: Optional path to save the JSON output
            
        Returns:
            Dictionary containing all OCR results
        """
        start_time = time.time()
        logger.info(f"Starting to process: {pdf_path}")
        
        try:
            # Validate PDF exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Create temporary directory
            self._create_temp_dir()
            
            # Convert PDF to images
            image_paths = self.convert_pdf_to_images(pdf_path)
            
            # Process each image
            results = []
            for i, image_path in enumerate(image_paths, 1):
                logger.info(f"Processing page {i}/{len(image_paths)}")
                page_result = self.process_image(image_path, i)
                results.append(page_result)
            
            # Prepare final output
            output = {
                "filename": os.path.basename(pdf_path),
                "total_pages": len(image_paths),
                "processing_time": time.time() - start_time,
                "pages": results
            }
            
            # Save to file if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                logger.info(f"Results saved to: {output_path}")
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
            
        finally:
            self._cleanup_temp_dir()

def main():
    """Main function to run the PDF parser."""
    if len(sys.argv) not in [2, 3]:
        print("Usage: python pdf_parser.py <input_pdf> [output_json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    
    try:
        parser = PDFParser(use_gpu=False)  # Set to True if GPU is available
        results = parser.parse_pdf(pdf_path, output_path)
        
        if not output_path:
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
