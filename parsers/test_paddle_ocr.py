from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', ocr_version='PP-OCRv4')

image_path = '/Users/santhosh/Desktop/Intern/pdf_parser_accelerator/pdf_parser_project/shared/input_pdfs/WhatsApp Image 2025-05-17 at 2.22.25 PM.jpeg'
ocr_result = ocr.ocr(image_path, cls=True)

# Save OCR result to file
with open("ocr_output.txt", "w", encoding="utf-8") as f:
    for line in ocr_result:
        if isinstance(line, list):
            for item in line:
                f.write(str(item) + '\n')
        else:
            f.write(str(line) + '\n')

print("OCR complete! Output saved to ocr_output.txt")
