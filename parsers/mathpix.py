import sys
print("PYTHONPATH:", sys.path)
import requests
import time
import os
import json

APP_ID = 'your_app_id'      # Replace with your Mathpix APP ID
APP_KEY = 'your_app_key'    # Replace with your Mathpix APP KEY

PDF_FILE = '/Users/santhosh/Desktop/Intern/pdf_parser_accelerator/pdf_parser_project/fundamental_quantum_equations.pdf'  # Local PDF path
BASE_URL = 'https://api.mathpix.com/v3/pdf'
OUTPUT_DIR = 'mathpix_outputs'
POLL_INTERVAL = 10  # seconds

def upload_pdf(file_path):
    headers = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
    }

    options_json = {
        "conversion_formats": {
            "docx": False,
            "tex.zip": False
        },
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True
    }

    files = {
        'file': open(file_path, 'rb'),
        'options_json': (None, str(options_json), 'application/json')
    }

    print("Uploading PDF to Mathpix...")
    response = requests.post(BASE_URL, headers=headers, files=files)
    response.raise_for_status()

    pdf_id = response.json().get('pdf_id')
    print(f"Uploaded. PDF ID: {pdf_id}")
    return pdf_id

def poll_status(pdf_id):
    status_url = f'{BASE_URL}/{pdf_id}'
    headers = {
        'app_id': APP_ID,
        'app_key': APP_KEY
    }

    print("Polling for processing status...")
    while True:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        status = response.json().get('status')

        print(f"Status: {status}")
        if status == 'completed':
            break
        elif status == 'error':
            raise Exception("Mathpix returned an error during processing.")
        time.sleep(POLL_INTERVAL)

def download_json(pdf_id, extension):
    url = f"{BASE_URL}/{pdf_id}.{extension}"
    headers = {
        'app_id': APP_ID,
        'app_key': APP_KEY
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{pdf_id}.{extension}")
    
    print(f"Downloading {extension} to {out_path}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    with open(out_path, 'wb') as f:
        f.write(response.content)
    print(f"Saved JSON: {out_path}")

def main():
    pdf_id = upload_pdf(PDF_FILE)
    poll_status(pdf_id)

    # Only download JSON formats
    json_formats = [
        'lines.json',
        'lines.mmd.json'
    ]

    for fmt in json_formats:
        try:
            download_json(pdf_id, fmt)
        except Exception as e:
            print(f"Failed to download {fmt}: {e}")

if __name__ == '__main__':
    main()
