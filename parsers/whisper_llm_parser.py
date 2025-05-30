import time
import requests
import urllib.parse
import sys
import json
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

# API Constants
WHISPER_API_BASE = "https://llmwhisperer-api.us-central.unstract.com/api/v2"
API_KEY = "1W-ET4pfPeESprxzyX-O8n0s-90kCgiaDbZXF5_HD4Y"  # replace with your actual key

# Timeout and retry settings
MAX_POLLING_ATTEMPTS = 60  # 5 minutes at 5-second intervals
POLLING_INTERVAL = 5  # seconds
REQUEST_TIMEOUT = 30  # seconds for HTTP requests

def submit_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Submit a PDF for processing with the LLM Whisperer API.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        API response as a dictionary

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        requests.RequestException: If the API call fails
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

    pdf_size = os.path.getsize(pdf_path) / (1024 * 1024)  # Size in MB
    logging.info(f"Submitting PDF: {pdf_path} (Size: {pdf_size:.2f} MB)")

    with open(pdf_path, "rb") as f:
        try:
            response = requests.post(
                f"{WHISPER_API_BASE}/whisper?mode=form&output_mode=layout_preserving",
                headers={
                    "Content-Type": "application/octet-stream",
                    "unstract-key": API_KEY
                },
                data=f,
                timeout=REQUEST_TIMEOUT
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Validate response format
            result = response.json()
            if "whisper_hash" not in result:
                raise ValueError("API response missing required 'whisper_hash' field")

            logging.info(f"PDF submitted successfully. Status code: {response.status_code}")
            logging.debug(f"Submit response: {json.dumps(result, indent=2)}")
            return result

        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = response.json()
            except json.JSONDecodeError:
                error_detail = response.text[:200] + "..." if len(response.text) > 200 else response.text

            logging.error(f"HTTP error during submission: {e}")
            logging.error(f"Response details: {error_detail}")
            raise

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise

def poll_for_status(whisper_hash: str) -> Dict[str, Any]:
    """
    Poll the API for the processing status of a submitted job.

    Args:
        whisper_hash: The hash returned from job submission

    Returns:
        The final status response as a dictionary

    Raises:
        TimeoutError: If polling exceeds the maximum attempts
        RuntimeError: If the job fails during processing
    """
    encoded_hash = urllib.parse.quote(whisper_hash, safe='')
    status_url = f"{WHISPER_API_BASE}/whisper-status/{encoded_hash}"
    headers = {"unstract-key": API_KEY}

    logging.info(f"Starting to poll for job status. Hash: {whisper_hash}")

    last_status = None
    for attempt in range(MAX_POLLING_ATTEMPTS):
        try:
            response = requests.get(
                status_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                current_status = data.get("status")

                # Only log when status changes to reduce verbosity
                if current_status != last_status:
                    logging.info(f"Job status: {current_status}")
                    last_status = current_status
                else:
                    logging.debug(f"Polling attempt {attempt+1}, status: {current_status}")

                # Handle different status values
                if current_status == "completed":
                    logging.info(f"Job completed successfully after {attempt+1} polling attempts")
                    return data
                elif current_status == "failed":
                    error_msg = data.get("error_message", "No error details provided")
                    logging.error(f"Job failed. Error: {error_msg}")
                    raise RuntimeError(f"Job failed during processing: {error_msg}")
                # Other statuses like "processing" or "queued" continue polling
            else:
                logging.warning(f"Attempt {attempt+1}: Unexpected status code {response.status_code}")
                logging.debug(f"Response body: {response.text[:200]}")

        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt+1}: Network error during polling: {e}")
        except json.JSONDecodeError:
            logging.warning(f"Attempt {attempt+1}: Could not decode JSON response.")

        # Wait before next polling attempt
        time.sleep(POLLING_INTERVAL)

    raise TimeoutError(f"Timed out waiting for job to complete after {MAX_POLLING_ATTEMPTS * POLLING_INTERVAL} seconds")

def retrieve_result(whisper_hash: str) -> Dict[str, Any]:
    """
    Retrieve the final result of a completed job.

    Args:
        whisper_hash: The hash returned from job submission

    Returns:
        The job results as a dictionary
    """
    encoded_hash = urllib.parse.quote(whisper_hash, safe='')
    retrieve_url = f"{WHISPER_API_BASE}/whisper-retrieve/{encoded_hash}"
    headers = {"unstract-key": API_KEY}

    logging.info(f"Retrieving final result for hash: {whisper_hash}")

    try:
        response = requests.get(
            retrieve_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        result = response.json()

        # Validate result has expected structure
        if "content" not in result:
            logging.warning("Result may be incomplete - missing 'content' field")

        content_size = len(json.dumps(result))
        logging.info(f"Successfully retrieved result (size: {content_size/1024:.2f} KB)")
        logging.debug(f"Result structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")

        return result

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve result: {e}")
        raise
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response during result retrieval.")
        logging.debug(f"Response text: {response.text}")
        raise

def main(input_pdf: str, output_json: str) -> None:
    """
    Main function to process a PDF through the LLM Whisperer API.

    Args:
        input_pdf: Path to the input PDF file
        output_json: Path where to save the output JSON
    """
    start_time = time.time()
    logging.info(f"Starting PDF processing job for {input_pdf}")

    try:
        # Step 1: Submit the PDF for processing
        job_response = submit_pdf(input_pdf)
        whisper_hash = job_response.get("whisper_hash")
        logging.info(f"Job submitted successfully. Hash: {whisper_hash}")

        # Step 2: Poll for job completion
        poll_for_status(whisper_hash)

        # Step 3: Retrieve and save the results
        result = retrieve_result(whisper_hash)

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        elapsed_time = time.time() - start_time
        logging.info(f"Job completed successfully in {elapsed_time:.2f} seconds")
        logging.info(f"Results saved to {output_json}")

    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except (requests.exceptions.RequestException, RuntimeError, TimeoutError, ValueError) as e:
        logging.error(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python whisper_llm_parser.py <input_pdf> <output_json>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    main(input_pdf, output_json)