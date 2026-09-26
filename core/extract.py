"""
PDF Range Extraction and Splitting Utilities.
"""

import os
import zipfile
from pathlib import Path
from typing import List, Union, Dict, Any
from pypdf import PdfReader, PdfWriter


def parse_ranges(ranges_str: str, total_pages: int, clamp: bool = True) -> List[int]:
    """
    Parses a page range string (e.g., '1-5, 8, 10-12') and returns a list of 0-indexed page indices.
    If ranges_str is empty/whitespace, returns all pages.

    Args:
        ranges_str: String specification of ranges.
        total_pages: Total number of pages in the PDF document.
        clamp: If True, silently constrains values to [1, total_pages].
               If False, raises ValueError for out-of-bounds or invalid ranges.
    """
    if not ranges_str or not ranges_str.strip():
        return list(range(total_pages))

    cleaned = ranges_str.strip()
    pages: List[int] = []
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]

    if not parts:
        return list(range(total_pages))

    for part in parts:
        if "-" in part:
            subparts = part.split("-", 1)
            start_str, end_str = subparts[0].strip(), subparts[1].strip()

            try:
                start = int(start_str) if start_str else 1
                end = int(end_str) if end_str else total_pages
            except ValueError:
                raise ValueError(f"Invalid range component: '{part}'")

            if start > end:
                if not clamp:
                    raise ValueError(f"Start page ({start}) cannot exceed end page ({end}) in '{part}'")
                # Normalize reversed range
                start, end = end, start

            if clamp:
                start = max(1, min(start, total_pages))
                end = max(1, min(end, total_pages))
                if start <= end:
                    pages.extend(range(start - 1, end))
            else:
                if start < 1 or end > total_pages:
                    raise ValueError(f"Range '{part}' is out of bounds (document has {total_pages} pages)")
                pages.extend(range(start - 1, end))
        else:
            try:
                page = int(part)
            except ValueError:
                raise ValueError(f"Invalid page number: '{part}'")

            if clamp:
                if 1 <= page <= total_pages:
                    pages.append(page - 1)
            else:
                if page < 1 or page > total_pages:
                    raise ValueError(f"Page {page} is out of bounds (document has {total_pages} pages)")
                pages.append(page - 1)

    # Deduplicate while preserving order
    return list(dict.fromkeys(pages))


def extract_pages(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    ranges: Union[str, List[int]],
    clamp: bool = True
) -> Dict[str, Any]:
    """
    Extracts pages from input_path and saves to output_path.
    ranges can be a string ('1-5, 8') or a pre-computed list of 0-indexed integers.
    """
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {in_p}")

    reader = PdfReader(str(in_p))
    total_pages = len(reader.pages)

    if isinstance(ranges, str):
        page_indices = parse_ranges(ranges, total_pages, clamp=clamp)
    else:
        page_indices = ranges

    if not page_indices:
        raise ValueError("No valid pages were specified for extraction.")

    writer = PdfWriter()
    for idx in page_indices:
        if 0 <= idx < total_pages:
            writer.add_page(reader.pages[idx])

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "wb") as f:
        writer.write(f)
    writer.close()

    return {
        "status": "success",
        "input": str(in_p),
        "output": str(out_p),
        "pages_extracted": len(page_indices),
        "total_source_pages": total_pages,
        "output_size_bytes": out_p.stat().st_size
    }


def split_pages(
    input_path: Union[str, Path],
    output_zip_path: Union[str, Path],
    ranges_str: str,
    clamp: bool = True
) -> Dict[str, Any]:
    """
    Splits ranges or individual pages into separate PDF files and zips them.
    If ranges_str contains comma-separated ranges (e.g. '1-5, 6-10'), each part becomes a PDF.
    If ranges_str is empty, splits every single page into its own PDF.
    """
    in_p = Path(input_path)
    out_zip = Path(output_zip_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input PDF does not exist: {in_p}")

    reader = PdfReader(str(in_p))
    total_pages = len(reader.pages)

    raw_parts = [p.strip() for p in ranges_str.split(",") if p.strip()] if ranges_str else []
    if not raw_parts:
        # Default: split every single page
        raw_parts = [str(i) for i in range(1, total_pages + 1)]

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = out_zip.parent / f"split_staging_{os.getpid()}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    created_files: List[Path] = []
    try:
        for idx, part in enumerate(raw_parts, start=1):
            pages_to_extract = parse_ranges(part, total_pages, clamp=clamp)
            if not pages_to_extract:
                continue

            writer = PdfWriter()
            for p_num in pages_to_extract:
                writer.add_page(reader.pages[p_num])

            clean_part_name = part.replace(" ", "").replace("-", "_to_")
            part_filename = f"{in_p.stem}_part_{idx:02d}_pages_{clean_part_name}.pdf"
            part_filepath = temp_dir / part_filename

            with open(part_filepath, "wb") as pf:
                writer.write(pf)
            writer.close()
            created_files.append(part_filepath)

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for f in created_files:
                zipf.write(f, arcname=f.name)

    finally:
        for f in created_files:
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass
        try:
            temp_dir.rmdir()
        except Exception:
            pass

    return {
        "status": "success",
        "output_zip": str(out_zip),
        "parts_count": len(created_files),
        "total_source_pages": total_pages,
        "output_size_bytes": out_zip.stat().st_size
    }
