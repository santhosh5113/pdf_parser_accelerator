import sys
import json
import re
from parsers.donut_parser import DonutParser

def detect_math_in_text(text, math_symbols):
    if not text:
        return 0
    math_count = 0
    for symbol in math_symbols:
        math_count += text.count(symbol)
    # LaTeX patterns
    latex_patterns = [
        r'\\frac', r'\\sum', r'\\int', r'\\sqrt', r'\\alpha', r'\\beta', r'\\gamma', 
        r'\\pi', r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\exp', r'\\leq', r'\\geq', 
        r'\\neq', r'\\approx', r'\\cdot', r'\\times', r'\\pm', r'\\infty', r'\\partial'
    ]
    for pattern in latex_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        math_count += len(matches)
    dollar_matches = re.findall(r'\$[^$]+\$', text)
    math_count += len(dollar_matches) * 2
    equation_patterns = [
        r'\\begin\{equation\}', r'\\\[.*?\\\]', r'\\\(.+?\\\)'
    ]
    for pattern in equation_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        math_count += len(matches)
    return math_count

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python donut_math_detect.py <pdf_path>"}))
        sys.exit(1)
    pdf_path = sys.argv[1]
    math_symbols = ['+', '=', '\\frac', '\\sum', '\\int', '\\sqrt', '\\alpha', '\\beta', '\\gamma', '\\pi', '\\theta', '\\infty', '\\partial', '\\leq', '\\geq', '\\neq', '\\approx']
    try:
        parser = DonutParser()
        results = parser.parse_pdf(pdf_path)
        total_math = 0
        for page in results:
            content = page.get("content", {})
            if isinstance(content, dict):
                text = json.dumps(content)
            else:
                text = str(content)
            total_math += detect_math_in_text(text, math_symbols)
        print(json.dumps({"math_count": total_math}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main() 