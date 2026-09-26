"""
PDF to DOCX Conversion Module.
"""

import time
from pathlib import Path
from typing import Union, Dict, Any, Optional
from pdf2docx import Converter


def convert_pdf_to_docx(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    start_page: int = 0,
    end_page: Optional[int] = None
) -> Dict[str, Any]:
    """
    Converts a PDF file to an editable Microsoft Word (.docx) document.

    Args:
        input_path: Path to source PDF.
        output_path: Path to target .docx file.
        start_page: 0-indexed start page (inclusive).
        end_page: 0-indexed end page (exclusive). None for end of file.
    """
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input file not found: {in_p}")

    out_p.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    cv = None
    try:
        cv = Converter(str(in_p))
        cv.convert(str(out_p), start=start_page, end=end_page)
    finally:
        if cv is not None:
            cv.close()

    duration = time.time() - t0
    out_size = out_p.stat().st_size if out_p.exists() else 0

    return {
        "status": "success",
        "input": str(in_p),
        "output": str(out_p),
        "output_size_bytes": out_size,
        "duration_seconds": round(duration, 2)
    }
