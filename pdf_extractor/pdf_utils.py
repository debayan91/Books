"""
Legacy pdf_utils compatibility module inside pdf_extractor.
Delegates to root core package.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import core

parse_ranges = core.parse_ranges
merge_pdfs = core.merge_pdfs
extract_pages = core.extract_pages
extract_and_merge = core.extract_and_merge
split_pages = core.split_pages
compress_pdf = core.compress_pdf
get_pdf_info = core.get_pdf_info
