import os
import sys
import time
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python parsers/llama_parser.py <input_pdf_path> <output_json_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_json = sys.argv[2]

    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("Error: LLAMA_CLOUD_API_KEY is not set in environment variables.")
        sys.exit(1)

    # 1. Upload PDF and get job_id
    with open(input_pdf, "rb") as f:
        files = {"file": (os.path.basename(input_pdf), f, "application/pdf")}
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"preset": "premium"}  # Set parsing mode to premium
        response = requests.post(
            "https://api.cloud.llamaindex.ai/api/parsing/upload",
            headers=headers,
            files=files,
            data=data
        )
        resp_json = response.json()
        if "id" not in resp_json:
            print("Upload failed, response:", resp_json)
            sys.exit(1)
        job_id = resp_json["id"]
        print("Job ID:", job_id)

    # 2. Poll for result
    result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/json"
    while True:
        result = requests.get(result_url, headers=headers)
        try:
            result_json = result.json()
        except Exception:
            result_json = {}
        if result.status_code == 200 and "pages" in result_json:
            break
        print("Waiting for parsing to complete...")
        print("Current response:", result_json)
        time.sleep(2)

    # 3. Save the result
    with open(output_json, "w", encoding="utf-8") as out:
        out.write(result.text)
    print(f"Successfully saved output to {output_json}")

    status_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"
    status_resp = requests.post(status_url, headers=headers)
    print("Job status:", status_resp.text)

if __name__ == "__main__":
    main()


