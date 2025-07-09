# Install TexTeller if not already installed:
# pip install texteller

from texteller import TexTeller
from PIL import Image
import os

def latex_ocr_image(image_path):
    model = TexTeller()
    image = Image.open(image_path)
    result = model(image)
    return result['latex']

def latex_ocr_folder(folder_path):
    model = TexTeller()
    latex_results = {}
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            image_path = os.path.join(folder_path, fname)
            image = Image.open(image_path)
            result = model(image)
            latex_results[fname] = result['latex']
    return latex_results

# Example usage:
if __name__ == "__main__":
    # For a single image
    latex_code = latex_ocr_image("path/to/equation_image.png")
    print("LaTeX:", latex_code)

    # For a folder of images
    results = latex_ocr_folder("path/to/equation_images/")
    for fname, latex in results.items():
        print(f"{fname}: {latex}")
