#!/usr/bin/env python3
"""
3-Up A4 Landscape PDF Converter.
Converts PDFs into A4 landscape sheets with 3 pages arranged horizontally.
Useful for economical reading and compact booklet printing.
"""

import sys
import argparse
from pathlib import Path
import core


def main():
    parser = argparse.ArgumentParser(description="Convert PDFs to 3-Up A4 landscape sheets.")
    parser.add_argument("-i", "--input", default="input", help="Input PDF file or directory (default: 'input').")
    parser.add_argument("-o", "--output", default="output", help="Output PDF file or directory (default: 'output').")
    parser.add_argument("--cols", type=int, default=3, help="Pages per sheet (default: 3).")

    args = parser.parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    if in_path.is_file():
        out_file = out_path if out_path.suffix == ".pdf" else out_path / f"{in_path.stem}_{args.cols}up_a4.pdf"
        print(f"Processing {in_path.name} -> {out_file.name}...")
        res = core.create_nup_pdf(in_path, out_file, pages_per_sheet=args.cols)
        print(f"Done! {res['original_pages']} source pages converted to {res['output_sheets']} sheets ({res['paper_savings_pct']}% paper saved).")
    else:
        print(f"Batch processing all PDFs in '{in_path}' -> '{out_path}'...")
        results = core.batch_create_3up(in_path, out_path)
        print(f"Batch completed: processed {len(results)} file(s).")


if __name__ == "__main__":
    main()
