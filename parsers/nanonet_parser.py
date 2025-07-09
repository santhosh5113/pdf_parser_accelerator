import sys
import os
import json
from pdf2image import convert_from_path
from PIL import Image
from transformers import AutoTokenizer, AutoProcessor, AutoModelForImageTextToText
import torch

def ocr_page_with_nanonets_s(image_path, model, processor, max_new_tokens=4096):
    prompt = (
        "Extract the text from the above document as if you were reading it naturally. "
        "Return the tables in html format. Return the equations in LaTeX representation. "
        "If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. "
        "Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. "
        "Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. "
        "Prefer using ☐ and ☑ for check boxes."
    )
    image = Image.open(image_path)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {"type": "image", "image": f"file://{image_path}"},
            {"type": "text", "text": prompt},
        ]},
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
    inputs = inputs.to(model.device)
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    # Remove prompt tokens from output
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
    output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return output_text[0]

def main():
    if len(sys.argv) != 3:
        print("Usage: python nanonets_ocr_s_parser.py <input_pdf> <output_json>")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    # Load model and processor
    model_path = "nanonets/Nanonets-OCR-s"
    print("Loading model and processor (this may take a while the first time)...")
    model = AutoModelForImageTextToText.from_pretrained(
        model_path, torch_dtype="auto", device_map="auto"
    )
    model.eval()
    processor = AutoProcessor.from_pretrained(model_path)

    # Convert PDF to images
    images = convert_from_path(input_pdf)
    temp_dir = os.path.splitext(output_json)[0] + "_pages"
    os.makedirs(temp_dir, exist_ok=True)
    results = []
    for idx, img in enumerate(images):
        img_path = os.path.join(temp_dir, f"page_{idx+1}.png")
        img.save(img_path, "PNG")
        print(f"Processing page {idx+1}...")
        page_markdown = ocr_page_with_nanonets_s(img_path, model, processor, max_new_tokens=15000)
        results.append({
            "page": idx + 1,
            "markdown": page_markdown
        })
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Parsed output saved to {output_json}")

if __name__ == "__main__":
    main() 