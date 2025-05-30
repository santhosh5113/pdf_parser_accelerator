# PDF Parser Accelerator

A powerful and flexible pipeline to accelerate PDF parsing, supporting scanned and native PDFs with advanced table and text extraction.

## Features

- Supports parsing of scanned PDFs using OCR-based models
- Extracts structured tables and complex layouts
- Handles native PDFs with precise text extraction
- Modular design allowing easy extension and integration
- Compatible with multiple vector databases for enhanced data storage and retrieval

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/pdf-parser-accelerator.git
cd pdf-parser-accelerator
Create and activate a virtual environment (optional but recommended):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Usage
Run the main pipeline with a sample PDF file:

bash
Copy
Edit
python run_pipeline.py --input path/to/sample.pdf
Project Structure
docling/ — Custom parser module for tables and layouts

paddleocr_parser.py — OCR-based parsing pipeline

llama_parse.py — Native text parsing module

run_pipeline.py — Main entry point for the pipeline

Contributing
Contributions are welcome! Please open issues or submit pull requests for bug fixes and feature requests.

License
This project is licensed under the MIT License. See the LICENSE file for details.


