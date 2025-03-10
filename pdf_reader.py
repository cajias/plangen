#!/usr/bin/env python3
"""
PDF Reader Tool - Extract text from PDF files
"""

import argparse
import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 library not found. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2


def extract_text_from_pdf(pdf_path, start_page=0, end_page=None):
    """Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        start_page: First page to extract (0-indexed)
        end_page: Last page to extract (0-indexed, None for all pages)
    """
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)

            if end_page is None:
                end_page = num_pages - 1

            print(
                f"PDF has {num_pages} pages. Showing pages {start_page+1} to {end_page+1}.\n"
            )
            print("=" * 80)
            print(f"CONTENT OF {pdf_path}:")
            print("=" * 80)

            for page_num in range(start_page, min(end_page + 1, num_pages)):
                page = reader.pages[page_num]
                text = page.extract_text()

                print(f"\n--- Page {page_num + 1} ---\n")
                print(text)

            print("\n" + "=" * 80)
            return True
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--start", type=int, default=0, help="First page to extract (1-indexed)"
    )
    parser.add_argument("--end", type=int, help="Last page to extract (1-indexed)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: File '{pdf_path}' does not exist.")
        return 1

    # Convert to 0-based indexing
    start_page = args.start - 1 if args.start > 0 else 0
    end_page = args.end - 1 if args.end is not None else None

    success = extract_text_from_pdf(pdf_path, start_page, end_page)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
