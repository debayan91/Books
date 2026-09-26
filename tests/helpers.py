"""
Test helpers for generating synthetic PDFs.
"""

from pathlib import Path
from pypdf import PdfWriter
from reportlab.pdfgen import canvas


def create_test_pdf(filepath: Path, num_pages: int = 5, title: str = "Test Doc") -> Path:
    """Generates a multi-page test PDF file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(filepath))
    c.setTitle(title)
    for i in range(1, num_pages + 1):
        c.drawString(100, 750, f"{title} - Page {i}")
        c.drawString(100, 700, f"Sample text content on page {i}.")
        c.showPage()
    c.save()
    return filepath
