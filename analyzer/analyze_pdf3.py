"""
Requirements:
- open_clip_torch
- torch
- pdf2image
- pillow
- poppler (for pdf2image)

Usage:
    python analyze_pdf3.py <path_to_pdf> [--device cuda]
"""
import sys
import os
import argparse
from pdf2image import convert_from_path
import open_clip
import torch
from PIL import Image
import numpy as np

# Prompts for classification
PROMPTS = {
    "NATIVE TEXT": [
        "A digital PDF page with only typed text, no tables or math.",
        "A computer-generated document with paragraphs of text.",
        "A native PDF page full of text, no images, no tables, no equations.",
        "This is not a scanned document.",
        "This page does not contain tables.",
        "This page does not contain mathematical equations."
    ],
    "NATIVE TABLE": [
        "A digital PDF page with computer-generated tables.",
        "A native PDF page showing a table with rows and columns.",
        "A digital document with tabular data, no scanning artifacts.",
        "This is not a scanned document.",
        "This page does not contain heavy math equations.",
        "This page is not mostly text."
    ],
    "NATIVE MATH HEAVY": [
        "A digital PDF page with many computer-generated mathematical equations.",
        "A native PDF page full of typed math formulas and symbols.",
        "A digital document with complex math notation and equations.",
        "This is not a scanned document.",
        "This page does not contain tables.",
        "This page is not mostly plain text."
    ],
    "SCANNED TEXT": [
        "A scanned image of a page with only text, no tables or math.",
        "A blurry, photographed document with paragraphs of text.",
        "A scanned page full of text, no tables, no equations.",
        "This is not a digital PDF.",
        "This page does not contain tables.",
        "This page does not contain mathematical equations."
    ],
    "SCANNED TABLE": [
        "A scanned image of a page with a table.",
        "A blurry, photographed document showing tabular data.",
        "A scanned page with a table of rows and columns.",
        "This is not a digital PDF.",
        "This page does not contain heavy math equations.",
        "This page is not mostly text."
    ],
    "SCANNED MATH HEAVY": [
        "A scanned image of a page with many handwritten or printed math equations.",
        "A blurry, photographed document full of math formulas and symbols.",
        "A scanned page with complex mathematical notation.",
        "This is not a digital PDF.",
        "This page does not contain tables.",
        "This page is not mostly plain text."
    ]
}

def preprocess_image(img):
    # Convert to grayscale
    gray = img.convert('L')
    # Binarization (Otsu's thresholding is not in PIL, so use a fixed threshold)
    bw = gray.point(lambda x: 0 if x < 180 else 255, '1')
    # Contrast enhancement
    from PIL import ImageEnhance, ImageOps
    contrast = ImageEnhance.Contrast(bw.convert('L')).enhance(2.0)
    # Crop margins (auto-crop white space)
    bbox = contrast.getbbox()
    if bbox:
        cropped = contrast.crop(bbox)
    else:
        cropped = contrast
    # Convert back to RGB for CLIP
    return cropped.convert('RGB')

def classify_pdf_pages(pdf_path, device="cpu", save_results=True, model=None, preprocess=None, tokenizer=None):
    # Convert PDF pages to images with higher DPI
    print(f"Converting PDF to images: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)
    print(f"Total pages: {len(images)}")

    # Prepare prompts
    # Flatten prompts and keep mapping to class
    prompt_texts = []
    prompt_class_indices = []
    prompt_labels = list(PROMPTS.keys())
    for class_idx, class_label in enumerate(prompt_labels):
        for prompt in PROMPTS[class_label]:
            prompt_texts.append(prompt)
            prompt_class_indices.append(class_idx)

    # Encode prompts
    with torch.no_grad():
        text_tokens = tokenizer(prompt_texts).to(device)
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    results = []
    for idx, img in enumerate(images):
        # Enhanced preprocessing
        processed_img = preprocess_image(img)
        image_input = preprocess(processed_img).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            # similarity: shape (1, num_prompts)
            # Aggregate by class
            num_classes = len(prompt_labels)
            class_scores = torch.zeros(num_classes, device=device)
            for class_idx in range(num_classes):
                # Find indices for this class
                indices = [i for i, c in enumerate(prompt_class_indices) if c == class_idx]
                class_scores[class_idx] = image_features[0, indices].mean()
            pred_idx = class_scores.argmax().item()
            pred_label = prompt_labels[pred_idx]
            results.append({
                "page": idx+1,
                "prediction": pred_label,
                "probabilities": class_scores.squeeze().cpu().numpy().tolist(),
                "label_order": prompt_labels
            })
            print(f"Page {idx+1}: {pred_label}")

    if save_results:
        out_path = os.path.splitext(os.path.basename(pdf_path))[0] + "_clip_results.npy"
        np.save(out_path, results)
        print(f"Results saved to {out_path}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify PDF pages using OpenCLIP.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    parser.add_argument("--device", type=str, default="cpu", help="Device to use: cpu or cuda")
    parser.add_argument("--clip-model", type=str, default="ViT-B-32", choices=["ViT-B-32", "ViT-B-16", "ViT-L-14"], help="CLIP model to use (ViT-B-32, ViT-B-16, ViT-L-14)")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_path):
        print(f"File not found: {args.pdf_path}")
        sys.exit(1)

    # Model selection logic
    print(f"Loading OpenCLIP model: {args.clip_model}")
    model, _, preprocess = open_clip.create_model_and_transforms(args.clip_model, pretrained='openai')
    tokenizer = open_clip.get_tokenizer(args.clip_model)
    model = model.to(args.device)
    model.eval()

    # Pass model, preprocess, tokenizer to classify_pdf_pages
    classify_pdf_pages(args.pdf_path, device=args.device, save_results=True, model=model, preprocess=preprocess, tokenizer=tokenizer)
