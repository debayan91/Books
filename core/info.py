"""
PDF Metadata and Page Inspector.
"""

from pathlib import Path
from typing import Dict, Any, Union
from pypdf import PdfReader


def format_file_size(size_bytes: int) -> str:
    """Formats byte counts into human-readable strings."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def detect_paper_size(width_pt: float, height_pt: float, tolerance: float = 6.0) -> str:
    """Matches width and height against common paper sizes."""
    # Normalize orientation so min is width, max is height for comparison
    w, h = sorted([width_pt, height_pt])
    standard_sizes = {
        "A4": (595.28, 841.89),
        "A3": (841.89, 1190.55),
        "A5": (419.53, 595.28),
        "US Letter": (612.0, 792.0),
        "US Legal": (612.0, 1008.0),
        "Executive": (522.0, 756.0),
    }

    for name, (sw, sh) in standard_sizes.items():
        if abs(w - sw) <= tolerance and abs(h - sh) <= tolerance:
            return name

    # Custom
    return f"Custom ({w * 0.352778:.0f}x{h * 0.352778:.0f}mm)"


def get_pdf_info(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Extracts comprehensive metadata, page counts, and dimension info from a PDF.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_size_bytes = path.stat().st_size
    reader = PdfReader(str(path))

    is_encrypted = reader.is_encrypted
    total_pages = len(reader.pages)

    metadata: Dict[str, Any] = {}
    if reader.metadata:
        for key, val in reader.metadata.items():
            clean_key = key.lstrip("/")
            metadata[clean_key] = str(val) if val is not None else ""

    first_page_info = {}
    if total_pages > 0:
        p0 = reader.pages[0]
        box = p0.mediabox
        width_pt = float(box.width)
        height_pt = float(box.height)
        orientation = "Landscape" if width_pt > height_pt else "Portrait"
        paper_size = detect_paper_size(width_pt, height_pt)

        first_page_info = {
            "width_pt": round(width_pt, 2),
            "height_pt": round(height_pt, 2),
            "width_mm": round(width_pt * 0.352778, 1),
            "height_mm": round(height_pt * 0.352778, 1),
            "orientation": orientation,
            "paper_size": paper_size
        }

    return {
        "filename": path.name,
        "filepath": str(path.resolve()),
        "file_size_bytes": file_size_bytes,
        "file_size_human": format_file_size(file_size_bytes),
        "total_pages": total_pages,
        "is_encrypted": is_encrypted,
        "first_page": first_page_info,
        "title": metadata.get("Title", "") or path.stem,
        "author": metadata.get("Author", ""),
        "subject": metadata.get("Subject", ""),
        "creator": metadata.get("Creator", ""),
        "producer": metadata.get("Producer", ""),
        "creation_date": metadata.get("CreationDate", "")
    }
