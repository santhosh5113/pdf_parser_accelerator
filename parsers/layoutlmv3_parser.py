from pdf2image import convert_from_path
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import pytesseract
import torch
import json
import sys
import os
import logging
from typing import List, Dict, Any, Optional
import tempfile

class LayoutLMv3Parser:
    def __init__(self, model_name: str = "microsoft/layoutlmv3-base"):
        """
        Initialize the LayoutLMv3 parser.
        
        Args:
            model_name (str): Name or path of the pre-trained model
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            # Important: apply_ocr=False because we provide our own OCR tokens & boxes
            self.logger.info(f"Loading model: {model_name}")
            self.processor = LayoutLMv3Processor.from_pretrained(model_name, apply_ocr=False)
            self.model = LayoutLMv3ForTokenClassification.from_pretrained(model_name)
            self.model.eval()
            
            # Check if CUDA is available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.logger.info(f"Using device: {self.device}")
            
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            raise

    def normalize_box(self, box: List[int], width: int, height: int) -> List[int]:
        """
        Normalize bounding boxes to 0-1000 scale (LayoutLMv3 requirement).
        
        Args:
            box (List[int]): Original bounding box [x1, y1, x2, y2]
            width (int): Image width
            height (int): Image height
            
        Returns:
            List[int]: Normalized bounding box
        """
        return [
            min(max(0, int(1000 * box[0] / width)), 1000),
            min(max(0, int(1000 * box[1] / height)), 1000),
            min(max(0, int(1000 * box[2] / width)), 1000),
            min(max(0, int(1000 * box[3] / height)), 1000),
        ]

    def ocr_and_preprocess(self, image: Image) -> tuple[List[str], List[List[int]]]:
        """
        Perform OCR and preprocess the results.
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            tuple: (tokens, boxes) where tokens are the OCR text and boxes are normalized coordinates
        """
        try:
            # Convert image to RGB if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use pytesseract to get OCR tokens and bounding boxes
            ocr = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            tokens, boxes = [], []
            width, height = image.size

            for i in range(len(ocr["text"])):
                # Only process entries that have valid text and bounding boxes
                if (ocr["conf"][i] > 0 and  # Check confidence
                    ocr["text"][i].strip() and  # Check text is not empty
                    ocr["width"][i] > 0 and ocr["height"][i] > 0):  # Check box dimensions
                    
                    tokens.append(ocr["text"][i].strip())
                    box = [
                        ocr["left"][i],
                        ocr["top"][i],
                        ocr["left"][i] + ocr["width"][i],
                        ocr["top"][i] + ocr["height"][i],
                    ]
                    boxes.append(self.normalize_box(box, width, height))

            if not tokens:
                self.logger.warning("No valid text detected in the image")
                return [], []

            return tokens, boxes
            
        except Exception as e:
            self.logger.error(f"Error in OCR processing: {str(e)}")
            raise

    def parse_pdf(self, pdf_path: str, output_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse a PDF file and extract structured information.
        
        Args:
            pdf_path (str): Path to the input PDF file
            output_path (str, optional): Path to save the JSON output
            
        Returns:
            List[Dict[str, Any]]: Extracted information by page
        """
        try:
            # Convert PDF to images
            self.logger.info(f"Converting PDF to images: {pdf_path}")
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(
                    pdf_path,
                    output_folder=temp_dir,
                    fmt="png",
                    dpi=300
                )
            
            all_results = []
            total_pages = len(images)
            
            for i, image in enumerate(images):
                self.logger.info(f"Processing page {i+1}/{total_pages}")
                
                # Get OCR results
                tokens, boxes = self.ocr_and_preprocess(image)
                
                if not tokens:
                    self.logger.warning(f"No text found on page {i+1}")
                    all_results.append({
                        "page": i + 1,
                        "tokens": []
                    })
                    continue
                
                try:
                    # Prepare input for the model
                    encoding = self.processor(
                        image,
                        text=tokens,  # Changed from 'words' to 'text'
                        boxes=boxes,
                        truncation=True,
                        return_tensors="pt"
                    )
                    
                    # Move input to the same device as model
                    encoding = {k: v.to(self.device) for k, v in encoding.items()}

                    # Get model predictions
                    with torch.no_grad():
                        outputs = self.model(**encoding)

                    logits = outputs.logits
                    predicted_ids = torch.argmax(logits, dim=-1).squeeze().tolist()
                    
                    # Handle single-token case
                    if not isinstance(predicted_ids, list):
                        predicted_ids = [predicted_ids]

                    # Combine results
                    page_results = []
                    for token, box, pred_id in zip(tokens, boxes, predicted_ids):
                        page_results.append({
                            "text": token,
                            "bbox": box,
                            "label_id": pred_id,
                            "label": self.model.config.id2label.get(pred_id, "UNKNOWN")
                        })

                    all_results.append({
                        "page": i + 1,
                        "tokens": page_results
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing page {i+1}: {str(e)}")
                    all_results.append({
                        "page": i + 1,
                        "tokens": [],
                        "error": str(e)
                    })

            # Save results if output path is provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(all_results, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Results saved to: {output_path}")

            return all_results
            
        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            raise


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    if len(sys.argv) != 3:
        logger.error("Incorrect number of arguments")
        print("Usage: python parsers/layoutlmv3_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.exists(input_pdf):
        logger.error(f"PDF file not found: {input_pdf}")
        print(f"Error: PDF file '{input_pdf}' not found.")
        sys.exit(1)

    try:
        parser = LayoutLMv3Parser()
        parser.parse_pdf(input_pdf, output_json)
        print(f"✅ Parsing complete. Output written to: {output_json}")
        
    except Exception as e:
        logger.error(f"Error during parsing: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
