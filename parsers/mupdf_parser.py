import fitz
from typing import Dict, List, Optional, Tuple
import logging
import argparse
import json
import os
import sys

class MuPDFParser:
    """A PDF parser using PyMuPDF (fitz) library."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[int, str]:
        """
        Extract text from PDF file page by page.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[int, str]: Dictionary with page numbers as keys and extracted text as values
        """
        try:
            doc = fitz.open(file_path)
            text_by_page = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_by_page[page_num] = text
                
            doc.close()
            return text_by_page
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def get_pdf_metadata(self, file_path: str) -> Dict:
        """
        Extract metadata from the PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict: Dictionary containing PDF metadata
        """
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            doc.close()
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            raise
    
    def extract_images(self, file_path: str, output_dir: str) -> List[str]:
        """
        Extract images from the PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            output_dir (str): Directory to save extracted images
            
        Returns:
            List[str]: List of paths to extracted images
        """
        import os
        
        try:
            doc = fitz.open(file_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_idx, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.{base_image['ext']}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    image_paths.append(image_path)
            
            doc.close()
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Error extracting images: {str(e)}")
            raise
    
    def get_page_count(self, file_path: str) -> int:
        """
        Get the total number of pages in the PDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            int: Number of pages
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            return page_count
            
        except Exception as e:
            self.logger.error(f"Error getting page count: {str(e)}")
            raise
    
    def extract_text_with_coordinates(self, file_path: str) -> Dict[int, List[Dict]]:
        """
        Extract text with their coordinates from the PDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[int, List[Dict]]: Dictionary with page numbers as keys and list of text blocks with coordinates as values
        """
        try:
            doc = fitz.open(file_path)
            text_data = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                text_data[page_num] = []
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text_data[page_num].append({
                                    "text": span["text"],
                                    "bbox": span["bbox"],
                                    "font": span["font"],
                                    "size": span["size"]
                                })
            
            doc.close()
            return text_data
            
        except Exception as e:
            self.logger.error(f"Error extracting text with coordinates: {str(e)}")
            raise

    def parse_pdf(self, input_path: str, output_path: str) -> None:
        """
        Parse PDF and save results to output file.
        
        Args:
            input_path (str): Path to input PDF file
            output_path (str): Path to save output JSON
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Extract all information
            result = {
                "metadata": self.get_pdf_metadata(input_path),
                "page_count": self.get_page_count(input_path),
                "text_by_page": self.extract_text_from_pdf(input_path),
                "text_with_coordinates": self.extract_text_with_coordinates(input_path)
            }
            
            # Extract images if they exist
            images_dir = os.path.join(os.path.dirname(output_path), "images")
            try:
                image_paths = self.extract_images(input_path, images_dir)
                result["images"] = [os.path.relpath(path, os.path.dirname(output_path)) 
                                  for path in image_paths]
            except Exception as e:
                self.logger.warning(f"Could not extract images: {str(e)}")
                result["images"] = []
            
            # Save results to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Successfully parsed PDF and saved results to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            raise

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Parse PDF files using PyMuPDF")
    parser.add_argument("input_path", help="Path to the input PDF file")
    parser.add_argument("output_path", help="Path to save the output JSON file")
    parser.add_argument("--log-level", default="INFO", 
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Set the logging level")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=args.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create parser and process PDF
    pdf_parser = MuPDFParser()
    try:
        pdf_parser.parse_pdf(args.input_path, args.output_path)
        print(f"Successfully parsed PDF. Results saved to: {args.output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 