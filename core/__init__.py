"""
PDF Toolkit Core Library.
Production-grade utilities for PDF manipulation, imposition, and conversion.
"""

__version__ = "2.0.0"

from core.config import (
    BASE_DIR,
    TEMP_DIR,
    INPUT_DIR,
    OUTPUT_DIR,
    DEFAULT_PORT,
    DEFAULT_HOST,
    MAX_CONTENT_LENGTH,
    TEMP_FILE_TTL_HOURS
)

from core.extract import (
    parse_ranges,
    extract_pages,
    split_pages
)

from core.merge import (
    merge_pdfs,
    extract_and_merge
)

from core.imposition import (
    create_nup_pdf,
    batch_create_3up
)

from core.convert import (
    convert_pdf_to_docx
)

from core.compress import (
    compress_pdf
)

from core.info import (
    get_pdf_info,
    format_file_size,
    detect_paper_size
)

from core.cleanup import (
    cleanup_temp_files
)

__all__ = [
    "BASE_DIR",
    "TEMP_DIR",
    "INPUT_DIR",
    "OUTPUT_DIR",
    "DEFAULT_PORT",
    "DEFAULT_HOST",
    "MAX_CONTENT_LENGTH",
    "TEMP_FILE_TTL_HOURS",
    "parse_ranges",
    "extract_pages",
    "split_pages",
    "merge_pdfs",
    "extract_and_merge",
    "create_nup_pdf",
    "batch_create_3up",
    "convert_pdf_to_docx",
    "compress_pdf",
    "get_pdf_info",
    "format_file_size",
    "detect_paper_size",
    "cleanup_temp_files",
]
