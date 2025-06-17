import time
import sys
import json
import logging
import os
from unstract.llmwhisperer import LLMWhispererClientV2
from unstract.llmwhisperer.client_v2 import LLMWhispererClientException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

API_KEY = os.environ.get("LLMWHISPERER_API_KEY", "YOUR_API_KEY_HERE")  # Set your API key in env or here

# Timeout and retry settings
MAX_POLLING_ATTEMPTS = 60  # 5 minutes at 5-second intervals
POLLING_INTERVAL = 5  # seconds


def submit_pdf(client, pdf_path: str) -> str:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")
    pdf_size = os.path.getsize(pdf_path) / (1024 * 1024)
    logging.info(f"Submitting PDF: {pdf_path} (Size: {pdf_size:.2f} MB)")
    try:
        result = client.whisper(
            file_path=pdf_path,
            mode="form",
            output_mode="layout_preserving",
            wait_for_completion=False
        )
        whisper_hash = result.get("whisper_hash")
        if not whisper_hash:
            raise ValueError("API response missing required 'whisper_hash' field")
        logging.info(f"PDF submitted successfully. Hash: {whisper_hash}")
        return whisper_hash
    except LLMWhispererClientException as e:
        logging.error(f"Error submitting PDF: {e.error_message()}")
        raise

def poll_for_status(client, whisper_hash: str) -> None:
    logging.info(f"Polling for job status. Hash: {whisper_hash}")
    last_status = None
    for attempt in range(MAX_POLLING_ATTEMPTS):
        try:
            status = client.whisper_status(whisper_hash=whisper_hash)
            current_status = status.get("status")
            if current_status != last_status:
                logging.info(f"Job status: {current_status}")
                last_status = current_status
            if current_status == "completed":
                logging.info(f"Job completed after {attempt+1} polling attempts")
                return
            elif current_status == "failed":
                error_msg = status.get("error_message", "No error details provided")
                logging.error(f"Job failed. Error: {error_msg}")
                raise RuntimeError(f"Job failed during processing: {error_msg}")
        except LLMWhispererClientException as e:
            logging.warning(f"Attempt {attempt+1}: Error during polling: {e.error_message()}")
        time.sleep(POLLING_INTERVAL)
    raise TimeoutError(f"Timed out waiting for job to complete after {MAX_POLLING_ATTEMPTS * POLLING_INTERVAL} seconds")

def retrieve_result(client, whisper_hash: str) -> dict:
    logging.info(f"Retrieving result for hash: {whisper_hash}")
    try:
        result = client.whisper_retrieve(whisper_hash=whisper_hash)
        if "extraction" not in result:
            logging.warning("Result may be incomplete - missing 'extraction' field")
        return result
    except LLMWhispererClientException as e:
        logging.error(f"Failed to retrieve result: {e.error_message()}")
        raise

def main(input_pdf: str, output_json: str) -> None:
    start_time = time.time()
    logging.info(f"Starting PDF processing job for {input_pdf}")
    client = LLMWhispererClientV2(api_key=API_KEY)
    try:
        whisper_hash = submit_pdf(client, input_pdf)
        while True:
            status = client.whisper_status(whisper_hash=whisper_hash)
            if status["status"] == "processed":
                final_result = client.whisper_retrieve(whisper_hash=whisper_hash)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(final_result, f, indent=2, ensure_ascii=False)
                elapsed_time = time.time() - start_time
                logging.info(f"Job completed successfully in {elapsed_time:.2f} seconds")
                logging.info(f"Results saved to {output_json}")
                break
            elif status["status"] in ["unknown", "failed"]:
                error_msg = status.get("error_message", "Unknown or failed status")
                logging.error(f"Processing failed or unknown status. Error: {error_msg}")
                sys.exit(1)
            time.sleep(5)
    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except (LLMWhispererClientException, RuntimeError, TimeoutError, ValueError) as e:
        logging.error(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python whisper_llm_parser.py <input_pdf> <output_json>")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    main(input_pdf, output_json)