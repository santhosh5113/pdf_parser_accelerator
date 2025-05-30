'''from nougat import NougatModel

# Load the model
model = NougatModel.from_pretrained("facebook/nougat-base")

# Process a PDF
output = model.process_pdf("/Users/santhosh/Desktop/Intern/pdf_parser_accelerator/pdf_parser_project/fundamental_quantum_equations.pdf")

# Save the output as markdown
with open("output.md", "w", encoding="utf-8") as f:
    f.write(output)
'''
# parsers/nougat_parser.py

import sys
import os
from nougat import NougatModel

def main():
    if len(sys.argv) != 3:
        print("Usage: python nougat_parser.py <input_pdf_path> <output_md_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_path = sys.argv[2]

    print(f"📥 Processing with Nougat: {input_pdf}")
    print(f"📤 Output will be saved to: {output_path}")

    try:
        # Load model
        model = NougatModel.from_pretrained("facebook/nougat-base")

        # Process PDF
        output = model.process_pdf(input_pdf)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save as markdown
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)

        print("✅ Markdown saved successfully!")

    except Exception as e:
        print(f"❌ Error during Nougat processing: {e}")

if __name__ == "__main__":
    main()
