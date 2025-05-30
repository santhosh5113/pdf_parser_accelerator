from pdf2image import convert_from_path
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import pytesseract
import torch
import json
import sys
import os

class LayoutLMv3Parser:
    def __init__(self, model_name="microsoft/layoutlmv3-base"):
        # Important: apply_ocr=False because we provide our own OCR tokens & boxes
        self.processor = LayoutLMv3Processor.from_pretrained(model_name, apply_ocr=False)
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(model_name)
        self.model.eval()

    def normalize_box(self, box, width, height):
        # Normalize bounding boxes to 0-1000 scale (LayoutLMv3 requirement)
        return [
            int(1000 * box[0] / width),
            int(1000 * box[1] / height),
            int(1000 * box[2] / width),
            int(1000 * box[3] / height),
        ]

    def ocr_and_preprocess(self, image):
        # Use pytesseract to get OCR tokens and bounding boxes
        ocr = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        tokens, boxes = [], []
        width, height = image.size

        for i in range(len(ocr["text"])):
            text = ocr["text"][i].strip()
            if not text:
                continue
            tokens.append(text)
            box = [
                ocr["left"][i],
                ocr["top"][i],
                ocr["left"][i] + ocr["width"][i],
                ocr["top"][i] + ocr["height"][i],
            ]
            boxes.append(self.normalize_box(box, width, height))

        return tokens, boxes

    def parse_pdf(self, pdf_path):
        images = convert_from_path(pdf_path)
        all_results = []

        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}")
            tokens, boxes = self.ocr_and_preprocess(image)

            encoding = self.processor(
                words=tokens,     # <-- IMPORTANT: use 'words', not 'text'
                boxes=boxes,
                images=image,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=512,
            )

            with torch.no_grad():
                outputs = self.model(**encoding)

            logits = outputs.logits
            predicted_ids = torch.argmax(logits, dim=-1).squeeze().tolist()

            page_results = []
            for token, box, pred_id in zip(tokens, boxes, predicted_ids):
                page_results.append({"text": token, "bbox": box, "label_id": pred_id})

            all_results.append({"page": i + 1, "tokens": page_results})

        return all_results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parsers/layoutlmv3_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.exists(input_pdf):
        print(f"Error: PDF file '{input_pdf}' not found.")
        sys.exit(1)

    parser = LayoutLMv3Parser()
    results = parser.parse_pdf(input_pdf)

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Parsing complete. Output written to: {output_json}")

