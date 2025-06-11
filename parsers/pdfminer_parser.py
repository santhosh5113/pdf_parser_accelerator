import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextBox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFMinerParser:
    def __init__(self):
        """Initialize the PDFMiner parser."""
        pass

    def extract_text_from_page(self, page) -> List[Dict[str, Any]]:
        """Extract text and its properties from a single page.
        
        Args:
            page: PDFMiner page object
            
        Returns:
            List of dictionaries containing text and its properties
        """
        texts = []
        for element in page:
            if isinstance(element, LTTextBox):
                # Get coordinates
                x0, y0, x1, y1 = element.bbox
                
                # Extract text and font information
                text_content = element.get_text().strip()
                if text_content:
                    text_info = {
                        "text": text_content,
                        "bbox": {
                            "x0": round(x0, 2),
                            "y0": round(y0, 2),
                            "x1": round(x1, 2),
                            "y1": round(y1, 2)
                        }
                    }
                    texts.append(text_info)
        
        return texts

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Parse a PDF file and extract text with layout information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Validate PDF exists
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            logger.info(f"Starting to process: {pdf_path}")
            
            # Extract text from each page
            pages = []
            for page_num, page_layout in enumerate(extract_pages(str(pdf_path)), 1):
                logger.info(f"Processing page {page_num}")
                page_texts = self.extract_text_from_page(page_layout)
                
                if page_texts:
                    pages.append({
                        "page_number": page_num,
                        "texts": page_texts
                    })
                else:
                    logger.warning(f"No text found on page {page_num}")
            
            # Prepare output
            output = {
                "filename": pdf_path.name,
                "total_pages": len(pages),
                "pages": pages
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

def main():
    """Main function to run the PDF parser."""
    if len(sys.argv) != 3:
        print("Usage: python pdfminer_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    try:
        # Parse PDF
        parser = PDFMinerParser()
        results = parser.parse_pdf(input_pdf)
        
        # Save results
        output_dir = Path(output_json).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Results saved to: {output_json}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()