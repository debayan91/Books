"""
Legacy PDF Utils Wrapper.
Delegates all operations to the production-grade core package while preserving full backward compatibility.
"""

from typing import List, Union
from pathlib import Path
import core

# Backward-compatibility alias
def parse_page_ranges(range_str: str, max_pages: int) -> List[int]:
    """Parses range string like '1-5,8' and returns 0-indexed page numbers (strict mode)."""
    return core.parse_ranges(range_str, max_pages, clamp=False)

parse_ranges = core.parse_ranges

def get_pdf_info(filepath: Union[str, Path]):
    """Returns total number of pages in the PDF for backward compatibility."""
    info = core.get_pdf_info(filepath)
    return info["total_pages"]

def get_pdf_metadata(filepath: Union[str, Path]):
    """Returns full metadata dictionary."""
    return core.get_pdf_info(filepath)

def extract_pages(input_path: Union[str, Path], output_path: Union[str, Path], pages_0_indexed: Union[str, List[int]]):
    """Extracts specified 0-indexed pages from input_path and saves to output_path."""
    return core.extract_pages(input_path, output_path, pages_0_indexed, clamp=True)

merge_pdfs = core.merge_pdfs
extract_and_merge = core.extract_and_merge
split_pages = core.split_pages
compress_pdf = core.compress_pdf
