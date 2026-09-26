#!/usr/bin/env python3
"""
PDF to DOCX Converter.
Converts PDF documents into editable Microsoft Word (.docx) files.
"""

import sys
import argparse
from pathlib import Path
import core


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Word (.docx).")
    parser.add_argument("input", nargs="?", default="cloud.pdf", help="Input PDF file (default: cloud.pdf).")
    parser.add_argument("output", nargs="?", default=None, help="Output .docx file path (default: <input>.docx).")
    parser.add_argument("--start", type=int, default=0, help="0-based start page (default: 0).")
    parser.add_argument("--end", type=int, default=None, help="0-based end page (default: all).")

    args = parser.parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        print(f"[ERROR] Input file '{in_path}' does not exist.")
        sys.exit(1)

    out_path = Path(args.output) if args.output else in_path.with_suffix(".docx")

    print(f"Converting '{in_path.name}' to '{out_path.name}'...")
    res = core.convert_pdf_to_docx(in_path, out_path, start_page=args.start, end_page=args.end)
    print(f"[SUCCESS] Converted in {res['duration_seconds']}s. Output: {out_path}")


if __name__ == "__main__":
    main()