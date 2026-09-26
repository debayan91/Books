"""
PDF Merging Utilities.
"""

from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from pypdf import PdfReader, PdfWriter
from core.extract import parse_ranges


def merge_pdfs(
    pdf_paths: List[Union[str, Path]],
    output_path: Union[str, Path],
    add_bookmarks: bool = True
) -> Dict[str, Any]:
    """
    Merges multiple PDF files in sequential order.
    Optionally creates top-level bookmark entries named after each file.
    """
    if not pdf_paths:
        raise ValueError("At least one PDF file must be provided for merging.")

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()
    current_page_index = 0
    merged_summary = []

    for item in pdf_paths:
        p = Path(item)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

        reader = PdfReader(str(p))
        num_pages = len(reader.pages)
        if num_pages == 0:
            continue

        if add_bookmarks and len(pdf_paths) > 1:
            bookmark_title = p.stem.replace("_", " ").title()
            writer.add_outline_item(bookmark_title, current_page_index)

        for page in reader.pages:
            writer.add_page(page)

        merged_summary.append({
            "filename": p.name,
            "pages": num_pages,
            "start_page": current_page_index + 1,
            "end_page": current_page_index + num_pages
        })
        current_page_index += num_pages

    with open(out_p, "wb") as f:
        writer.write(f)
    writer.close()

    return {
        "status": "success",
        "output": str(out_p),
        "files_merged": len(merged_summary),
        "total_pages": current_page_index,
        "files_detail": merged_summary,
        "output_size_bytes": out_p.stat().st_size
    }


def extract_and_merge(
    files_data: List[Dict[str, Any]],
    output_path: Union[str, Path],
    clamp: bool = True
) -> Dict[str, Any]:
    """
    Extracts custom ranges from multiple PDFs and merges them in specified order.

    files_data format:
    [
        {"path": "/path/to/doc1.pdf", "ranges": "1-5", "title": "Optional Bookmark"},
        {"path": "/path/to/doc2.pdf", "ranges": "10-12", "title": "Section 2"}
    ]
    """
    if not files_data:
        raise ValueError("No files specified for extract and merge.")

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()
    current_page_index = 0
    processed_items = []

    for item in files_data:
        p = Path(item["path"])
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

        ranges_str = item.get("ranges", "")
        custom_title = item.get("title") or p.stem.replace("_", " ").title()

        reader = PdfReader(str(p))
        total_pages = len(reader.pages)

        page_indices = parse_ranges(ranges_str, total_pages, clamp=clamp)
        if not page_indices:
            continue

        if len(files_data) > 1:
            writer.add_outline_item(custom_title, current_page_index)

        for idx in page_indices:
            if 0 <= idx < total_pages:
                writer.add_page(reader.pages[idx])

        processed_items.append({
            "filename": p.name,
            "ranges": ranges_str,
            "extracted_count": len(page_indices),
            "start_page": current_page_index + 1,
            "end_page": current_page_index + len(page_indices)
        })
        current_page_index += len(page_indices)

    with open(out_p, "wb") as f:
        writer.write(f)
    writer.close()

    return {
        "status": "success",
        "output": str(out_p),
        "files_processed": len(processed_items),
        "total_pages": current_page_index,
        "detail": processed_items,
        "output_size_bytes": out_p.stat().st_size
    }
