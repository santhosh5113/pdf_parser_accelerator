import sys
import json
import logging
import camelot
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
import tempfile
import os
from typing import Dict, Any, List, Union
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CamelotParser:
    def __init__(self):
        """Initialize the Camelot parser."""
        self.temp_dir = None
        self.needs_cleanup = False

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.needs_cleanup:
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                self.needs_cleanup = False
            except Exception as e:
                logger.warning(f"Error cleaning up temporary files: {str(e)}")

    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Check if the PDF is scanned (image-based) or searchable.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            bool: True if the PDF is scanned, False if it's searchable
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page = pdf_reader.pages[0]
                text = page.extract_text()
                
                # If there's very little text or no text, likely a scanned PDF
                return len(text.strip()) < 100
        except Exception as e:
            logger.warning(f"Error checking PDF type: {str(e)}")
            return True

    def perform_ocr(self, pdf_path: str) -> str:
        """
        Perform OCR on a scanned PDF and return path to the searchable PDF.
        
        Args:
            pdf_path: Path to the scanned PDF file
            
        Returns:
            str: Path to the OCR'd PDF file
        """
        try:
            logger.info("Starting OCR process...")
            
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            self.needs_cleanup = True
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Process each page with OCR
            ocr_texts = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1} with OCR...")
                
                # Save image temporarily
                temp_img = os.path.join(self.temp_dir, f"page_{i}.png")
                image.save(temp_img)
                
                # Perform OCR
                text = pytesseract.image_to_string(temp_img)
                ocr_texts.append(text)
                
                # Clean up page image
                os.remove(temp_img)
            
            # Create a text file with OCR results
            ocr_text_path = os.path.join(self.temp_dir, "ocr_text.txt")
            with open(ocr_text_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(ocr_texts))
            
            logger.info("OCR process completed")
            return ocr_text_path
            
        except Exception as e:
            logger.error(f"Error in OCR process: {str(e)}")
            raise

    def extract_tables_from_page(self, tables) -> List[Dict[str, Any]]:
        """Extract tables and their properties from a single page.
        
        Args:
            tables: List of Camelot table objects
            
        Returns:
            List of dictionaries containing table data and properties
        """
        extracted_tables = []
        for idx, table in enumerate(tables, 1):
            # Get table coordinates from the table object directly
            coords = table._bbox
            
            # Convert table to dictionary format
            table_dict = table.df.to_dict('split')
            
            table_info = {
                "table_number": idx,
                "bbox": {
                    "x0": round(coords[0], 2),
                    "y0": round(coords[1], 2),
                    "x1": round(coords[2], 2),
                    "y1": round(coords[3], 2)
                },
                "accuracy": round(table.accuracy, 2),
                "whitespace": round(table.whitespace, 2),
                "columns": table.shape[1],
                "rows": table.shape[0],
                "data": {
                    "headers": table_dict['columns'],
                    "data": table_dict['data']
                }
            }
            extracted_tables.append(table_info)
        
        return extracted_tables

    def parse_pdf(self, pdf_path: str, flavor: str = 'lattice', pages: Union[str, List[int]] = 'all') -> Dict[str, Any]:
        """Parse a PDF file and extract tables with layout information.
        
        Args:
            pdf_path: Path to the PDF file
            flavor: Table parsing method ('lattice' or 'stream')
            pages: Page numbers to parse ('all' or list of numbers)
            
        Returns:
            Dictionary containing extracted tables and metadata
        """
        try:
            # Validate PDF exists
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            logger.info(f"Starting to process: {pdf_path}")
            
            # Check if PDF needs OCR
            ocr_text = None
            if self.is_scanned_pdf(str(pdf_path)):
                logger.info("Detected scanned PDF, performing OCR...")
                ocr_text_path = self.perform_ocr(str(pdf_path))
                with open(ocr_text_path, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
            
            logger.info(f"Using {flavor} method for parsing")
            
            # Extract tables from PDF
            tables = camelot.read_pdf(
                str(pdf_path),
                pages=str(pages),
                flavor=flavor
            )
            
            logger.info(f"Found {len(tables)} tables in the PDF")
            
            # Process each page
            pages_data = []
            current_page = None
            current_page_tables = []
            
            for table in tables:
                page_number = table.page
                
                if current_page != page_number:
                    # Save previous page data
                    if current_page is not None:
                        pages_data.append({
                            "page_number": current_page,
                            "tables": current_page_tables
                        })
                    # Start new page
                    current_page = page_number
                    current_page_tables = []
                
                # Add table to current page
                current_page_tables.extend(self.extract_tables_from_page([table]))
            
            # Add last page
            if current_page is not None:
                pages_data.append({
                    "page_number": current_page,
                    "tables": current_page_tables
                })
            
            # Prepare output
            output = {
                "filename": pdf_path.name,
                "total_pages": len(pages_data),
                "parser": "camelot",
                "flavor": flavor,
                "ocr_applied": self.needs_cleanup,  # Indicates if OCR was used
                "pages": pages_data
            }
            
            # Add OCR text if available
            if ocr_text:
                output["ocr_text"] = ocr_text
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
        finally:
            self.cleanup()

def main():
    """Main function to run the PDF parser."""
    if len(sys.argv) != 4:
        print("Usage: python <script_path> <input_pdf> <output_json>")
        sys.exit(1)

    script_path = sys.argv[0]  # Path to the script itself
    input_pdf = sys.argv[1]    # Input PDF path
    output_json = sys.argv[2]  # Output JSON path
    flavor = sys.argv[3] if len(sys.argv) > 3 else 'lattice'

    try:
        # Parse PDF
        parser = CamelotParser()
        results = parser.parse_pdf(input_pdf, flavor=flavor)
        
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