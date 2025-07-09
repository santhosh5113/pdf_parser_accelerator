import os
from typing import List, Dict, Any, Union
from PIL import Image
import requests

# Surya imports
from surya.layout import LayoutPredictor
from surya.texify import TexifyPredictor
from surya.ocr import run_ocr
from surya.model.detection.segformer import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor

def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Convert PDF to list of PIL Images."""
    from pdf2image import convert_from_path
    return convert_from_path(pdf_path)

def detect_formulas(page_img: Image.Image, layout_predictor: LayoutPredictor) -> List[Dict[str, Any]]:
    """Detect formula regions in a page image using Surya layout model."""
    layout_results = layout_predictor([page_img])
    formulas = []
    for region in layout_results[0]['bboxes']:
        if region['label'] == 'Formula':
            formulas.append(region)
    return formulas

def crop_formula_images(page_img: Image.Image, formulas: List[Dict[str, Any]]) -> List[Image.Image]:
    """Crop formula regions from a page image."""
    crops = []
    for region in formulas:
        x1, y1, x2, y2 = region['bbox']
        crops.append(page_img.crop((x1, y1, x2, y2)))
    return crops

def latex_ocr_on_images(images: List[Image.Image], texify_predictor: TexifyPredictor) -> List[str]:
    """Run LaTeX OCR on a list of images."""
    if not images:
        return []
    results = texify_predictor(images)
    return [r['latex'] for r in results]

def full_page_ocr(page_img: Image.Image, det_model, det_processor, rec_model, rec_processor) -> List[Dict[str, Any]]:
    """Run full-page OCR using Surya."""
    return run_ocr([page_img], [["en"]], det_model, det_processor, rec_model, rec_processor)[0]['text_lines']

def process_pdf_or_image(input_path: str) -> Dict[str, Any]:
    """Main pipeline: process a PDF or image, extract formulas and text."""
    # Prepare Surya models
    layout_predictor = LayoutPredictor()
    texify_predictor = TexifyPredictor()
    det_processor, det_model = load_det_processor(), load_det_model()
    rec_model, rec_processor = load_rec_model(), load_rec_processor()

    # Determine input type
    ext = os.path.splitext(input_path)[1].lower()
    if ext == '.pdf':
        pages = pdf_to_images(input_path)
    else:
        pages = [Image.open(input_path)]

    results = []
    for page_num, page_img in enumerate(pages):
        page_result = {'page': page_num+1, 'formulas': [], 'text_lines': []}
        # Layout analysis for formulas
        formulas = detect_formulas(page_img, layout_predictor)
        crops = crop_formula_images(page_img, formulas)
        latex_results = latex_ocr_on_images(crops, texify_predictor)
        for region, latex in zip(formulas, latex_results):
            page_result['formulas'].append({'bbox': region['bbox'], 'latex': latex})
        # Full-page OCR
        text_lines = full_page_ocr(page_img, det_model, det_processor, rec_model, rec_processor)
        page_result['text_lines'] = text_lines
        results.append(page_result)
    return {'input': input_path, 'pages': results}

def surya_ocr_api(file_path, api_key, endpoint="https://api.datalab.to/v1/ocr"):
    """
    Send a PDF or image to Surya OCR cloud API and return the result.
    """
    with open(file_path, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(endpoint, files=files, headers=headers)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    # --- User config ---
    API_KEY = "YOUR_API_KEY"  # <-- Replace with your actual API key
    INPUT_FILE = "small_dataset/01030000000001.pdf"  # PDF or image
    # -------------------

    result = surya_ocr_api(INPUT_FILE, API_KEY)
    # Print the result (or save/process as needed)
    import json
    print(json.dumps(result, indent=2))
