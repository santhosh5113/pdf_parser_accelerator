from pdf2image import convert_from_path
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import re
import json
import os
import sys
import logging
from typing import List, Dict, Any, Optional
import tempfile

class DonutParser:
    """Parser using the Donut (Document Understanding Transformer) model."""
    
    def __init__(self, model_name: str = "naver-clova-ix/donut-base-finetuned-cord-v2"):
    
        """
        Initialize the Donut parser.
        
        Args:
            model_name (str): Name or path of the pre-trained model
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            self.logger.info(f"Loading model: {model_name}")
            self.processor = DonutProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            # Set up device
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.logger.info(f"Using device: {self.device}")
            
            # Set model to evaluation mode
            self.model.eval()
            
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            raise

    def process_image(self, image: Image) -> Dict[str, Any]:
        """
        Process a single image using the Donut model.
        
        Args:
            image (PIL.Image): Input image to process
            
        Returns:
            Dict[str, Any]: Extracted information from the image
        """
        try:
            # Convert image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Prepare decoder input ids with task prompt
            task_prompt = "<s_cord-v2>"
            decoder_input_ids = self.processor.tokenizer(
                task_prompt,
                add_special_tokens=False,
                return_tensors="pt"
            ).input_ids

            # Prepare pixel values
            pixel_values = self.processor(image, return_tensors="pt").pixel_values

            # Generate output sequence
            with torch.no_grad():  # Disable gradient calculation for inference
                outputs = self.model.generate(
                    pixel_values.to(self.device),
                    decoder_input_ids=decoder_input_ids.to(self.device),
                    max_length=self.model.decoder.config.max_position_embeddings,
                    pad_token_id=self.processor.tokenizer.pad_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id,
                    use_cache=True,
                    bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                    return_dict_in_generate=True,
                    num_beams=4,  # Use beam search for better results
                    early_stopping=True
                )

            # Decode output sequence
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
            sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token

            # Convert sequence to structured output
            try:
                result = self.processor.token2json(sequence)
            except Exception as e:
                self.logger.warning(f"Error converting sequence to JSON: {str(e)}")
                result = {"raw_text": sequence}

            return result
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return {"error": str(e)}

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
                
                # Process the page
                result = self.process_image(image)
                
                # Add page information
                page_result = {
                    "page": i + 1,
                    "content": result
                }
                all_results.append(page_result)

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
        print("Usage: python parsers/donut_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.exists(input_pdf):
        logger.error(f"PDF file not found: {input_pdf}")
        print(f"Error: PDF file '{input_pdf}' not found.")
        sys.exit(1)

    try:
        parser = DonutParser()
        parser.parse_pdf(input_pdf, output_json)
        print(f"✅ Parsing complete. Output written to: {output_json}")
        
    except Exception as e:
        logger.error(f"Error during parsing: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
