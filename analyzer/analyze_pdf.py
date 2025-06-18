# analyze/analyze_pdf.py

import fitz  # PyMuPDF
import re
import os

def analyze_pdf(pdf_path: str) -> str:
    """Analyze PDF and determine its category using all pages and advanced table detection."""
    try:
        doc = fitz.open(pdf_path)
        has_text = False
        has_images = False
        has_tables = False
        table_like = False
        all_pages_no_text = True
        filename = os.path.basename(pdf_path).lower()

        # Try to import advanced table detectors
        try:
            import camelot
        except ImportError:
            camelot = None
        try:
            import pdfplumber
        except ImportError:
            pdfplumber = None

        for i, page in enumerate(doc):
            text = page.get_text()
            images = page.get_images()
            if text.strip():
                has_text = True
                all_pages_no_text = False
            if images:
                has_images = True
            # PyMuPDF table detection
            try:
                tables = page.find_tables()
                if tables is not None and tables.tables:
                    has_tables = True
                    print(f"[Page {i}] PyMuPDF found tables.")
            except Exception as e:
                pass
            # Heuristic for table-like text
            lines = text.splitlines()
            table_lines = [line for line in lines if ('|' in line or '\t' in line)]
            if len(table_lines) > 3:
                table_like = True
                print(f"[Page {i}] Table-like text detected.")

        doc.close()

        # Camelot table detection (on all pages)
        if camelot is not None:
            try:
                tables = camelot.read_pdf(pdf_path, pages="all")
                if tables and tables.n > 0:
                    has_tables = True
                    print(f"Camelot found {tables.n} tables.")
            except Exception as e:
                print(f"Camelot error: {e}")

        # pdfplumber table detection (on all pages)
        if pdfplumber is not None:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        extracted_tables = page.extract_tables()
                        if extracted_tables and len(extracted_tables) > 0:
                            has_tables = True
                            print(f"[pdfplumber] Page {i} has {len(extracted_tables)} tables.")
            except Exception as e:
                print(f"pdfplumber error: {e}")

        # Routing logic
        if has_tables or table_like:
            return "native_table"
        elif not has_text and has_images and ("table" in filename):
            return "native_table"
        elif all_pages_no_text and has_images:
            return "scanned_pdf"
        elif has_text:
            return "native_text"
        else:
            return "unknown"
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return "unknown"
