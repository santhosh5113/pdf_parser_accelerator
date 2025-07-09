import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

# Try importing vision_parse with helpful error message
try:
    from vision_parse import VisionParser
except ImportError:
    print("❌ Error: vision_parse module not found. Please install it first.")
    sys.exit(1)

# Available models and their characteristics
AVAILABLE_MODELS = {
    "llama3.2-vision:11b": {
        "description": "Smaller Llama 3.2 vision model",
        "size": "11B parameters",
        "local": True
    },
    "llama3.2-vision:70b": {
        "description": "Larger Llama 3.2 vision model",
        "size": "70B parameters",
        "local": True
    },
    "llava:13b": {
        "description": "Default LLaVA model, good all-round performance",
        "size": "13B parameters",
        "local": True
    },
    "llava:34b": {
        "description": "Larger LLaVA model",
        "size": "34B parameters",
        "local": True
    },
    "gpt-4o": {
        "description": "OpenAI GPT-4 Vision model",
        "size": "Requires API key",
        "local": False
    },
    "gpt-4o-mini": {
        "description": "OpenAI GPT-4 Vision mini model",
        "size": "Requires API key",
        "local": False
    },
    "gemini-1.5-flash": {
        "description": "Google Gemini 1.5 Flash model",
        "size": "Requires API key",
        "local": False
    },
    "gemini-2.0-flash-exp": {
        "description": "Google Gemini 2.0 Flash experimental model",
        "size": "Requires API key",
        "local": False
    },
    "gemini-1.5-pro": {
        "description": "Google Gemini 1.5 Pro model",
        "size": "Requires API key",
        "local": False
    },
    "deepseek-chat": {
        "description": "DeepSeek vision chat model",
        "size": "Requires API key",
        "local": False
    }
}

def list_available_models():
    """Print available models and their descriptions."""
    print("\n📋 Available Models:")
    for model, info in AVAILABLE_MODELS.items():
        print(f"\n🔹 {model}")
        print(f"   Description: {info['description']}")
        print(f"   Size: {info['size']}")
        print(f"   Local: {'Yes' if info.get('local') else 'No'}")

def check_ollama(model_name: str) -> bool:
    """Check if Ollama daemon is running and model is available."""
    try:
        # Check if Ollama process is running
        result = subprocess.run(['pgrep', 'ollama'], capture_output=True)
        if result.returncode != 0:
            print("❌ Error: Ollama daemon is not running. Please start it with 'ollama serve'")
            return False
        
        # Check if model is pulled
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if model_name not in result.stdout:
            print(f"❌ Error: {model_name} model not found. Please pull it first with 'ollama pull {model_name}'")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking Ollama status: {e}")
        return False

def validate_paths(pdf_path, output_path):
    """Validate input and output paths."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"Input file must be a PDF: {pdf_path}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Check if output path is writable
    try:
        with open(output_path, 'a') as f:
            pass
        os.remove(output_path)
    except IOError as e:
        raise IOError(f"Cannot write to output path: {output_path}. Error: {e}")

def main(pdf_path: str, output_path: str, model_name: str = "llava:13b", prompt: Optional[str] = None, concurrency: bool = False):
    """
    Process PDF using specified vision model.
    
    Args:
        pdf_path: Path to input PDF
        output_path: Path for output JSON
        model_name: Name of the model to use (default: llava:13b)
        prompt: Custom prompt for extraction
        concurrency: Enable concurrency
    """
    if model_name not in AVAILABLE_MODELS:
        print(f"❌ Error: Unknown model '{model_name}'")
        list_available_models()
        sys.exit(1)

    print(f"📥 Processing: {pdf_path}")
    print(f"🤖 Using model: {model_name}")
    print(f"📤 Output will be saved to: {output_path}")

    parser = None  # Initialize parser as None
    try:
        # Validate paths first
        validate_paths(pdf_path, output_path)
        
        # Check Ollama status only for local models
        if AVAILABLE_MODELS[model_name].get("local", False):
            if not check_ollama(model_name):
                sys.exit(1)

        parser = VisionParser(
            model_name=model_name,
            temperature=0,
            custom_prompt=prompt or "- Only use data found directly in the input. Do not add or invent details. If data is missing, leave it as null or \"Not Available\". Do not assume or correct data format unless it's clearly stated.",
            image_mode="url",
            detailed_extraction=True,
            enable_concurrency=concurrency,
        )

        markdown_pages = parser.convert_pdf(pdf_path)

        with open(output_path, "w", encoding='utf-8') as f:
            json.dump({"pages": markdown_pages}, f, indent=2, ensure_ascii=False)

        print("✅ PDF processed successfully!")

    except Exception as e:
        print(f"❌ Error during VisionParser execution: {str(e)}")
        sys.exit(1)
    finally:
        if parser and hasattr(parser, 'cleanup'):
            parser.cleanup()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="VisionParser PDF extraction")
    parser.add_argument("input_pdf", nargs="?", help="Path to input PDF")
    parser.add_argument("output_json", nargs="?", help="Path to output JSON")
    parser.add_argument("--model", default="llava:13b", help="Model name to use")
    parser.add_argument("--prompt", default=None, help="Custom prompt for extraction")
    parser.add_argument("--concurrency", action="store_true", help="Enable concurrency")
    parser.add_argument("--list-models", action="store_true", help="List available models and exit")
    args = parser.parse_args()

    if args.list_models:
        list_available_models()
        sys.exit(0)

    if not args.input_pdf or not args.output_json:
        parser.print_help()
        sys.exit(1)

    main(args.input_pdf, args.output_json, args.model, args.prompt, args.concurrency)
