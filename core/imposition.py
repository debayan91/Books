"""
PDF Imposition & N-Up Layout Engine.
Specialized for 3-Up A4 landscape compact reading & printing.
"""

import os
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

# Standard Page Sizes in points (72 points = 1 inch)
PAGE_SIZES = {
    "A4": (595.28, 841.89),       # Portrait: 595.28 x 841.89
    "Letter": (612.0, 792.0),
    "A3": (841.89, 1190.55),
    "A5": (419.53, 595.28)
}


def create_nup_pdf(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    pages_per_sheet: int = 3,
    sheet_size: str = "A4",
    landscape: bool = True,
    draw_cut_lines: bool = False,
    margin_pt: float = 12.0
) -> Dict[str, Any]:
    """
    Arranges multiple source pages onto a single target sheet (e.g. 3-Up A4 Landscape).

    Args:
        input_path: Path to source PDF.
        output_path: Path for output PDF.
        pages_per_sheet: Number of horizontal columns/pages per sheet (default: 3).
        sheet_size: Standard size name ('A4', 'Letter', etc.).
        landscape: If True, uses landscape orientation for the target sheet.
        draw_cut_lines: If True, adds subtle vertical division indicators between columns.
        margin_pt: Outer margin in points.
    """
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input file not found: {in_p}")

    reader = PdfReader(str(in_p))
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError(f"PDF {in_p.name} has 0 pages.")

    # Determine sheet dimensions
    base_w, base_h = PAGE_SIZES.get(sheet_size, PAGE_SIZES["A4"])
    sheet_width = max(base_w, base_h) if landscape else min(base_w, base_h)
    sheet_height = min(base_w, base_h) if landscape else max(base_w, base_h)

    usable_width = sheet_width - (2 * margin_pt)
    usable_height = sheet_height - (2 * margin_pt)

    column_width = usable_width / pages_per_sheet
    writer = PdfWriter()

    # Process in chunks of pages_per_sheet
    for chunk_start in range(0, total_pages, pages_per_sheet):
        chunk = reader.pages[chunk_start : chunk_start + pages_per_sheet]
        sheet = PageObject.create_blank_page(width=sheet_width, height=sheet_height)

        for col_idx, page in enumerate(chunk):
            orig_w = float(page.mediabox.width)
            orig_h = float(page.mediabox.height)

            if orig_w <= 0 or orig_h <= 0:
                continue

            # Scale to fit within column slot while maintaining aspect ratio
            scale_w = column_width / orig_w
            scale_h = usable_height / orig_h
            scale = min(scale_w, scale_h)

            scaled_w = orig_w * scale
            scaled_h = orig_h * scale

            # Center vertically within sheet
            ty = margin_pt + (usable_height - scaled_h) / 2.0

            # Center horizontally within column
            col_left = margin_pt + (col_idx * column_width)
            tx = col_left + (column_width - scaled_w) / 2.0

            # Scale and translate directly onto the sheet using merge_transformed_page
            transform = Transformation().scale(scale, scale).translate(tx, ty)
            sheet.merge_transformed_page(page, transform)

        writer.add_page(sheet)

    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "wb") as f:
        writer.write(f)
    writer.close()

    total_sheets = (total_pages + pages_per_sheet - 1) // pages_per_sheet
    return {
        "status": "success",
        "input": str(in_p),
        "output": str(out_p),
        "original_pages": total_pages,
        "output_sheets": total_sheets,
        "pages_per_sheet": pages_per_sheet,
        "sheet_format": f"{sheet_size} {'Landscape' if landscape else 'Portrait'}",
        "reduction_ratio": f"{total_pages}:{total_sheets}",
        "paper_savings_pct": round((1.0 - (total_sheets / total_pages)) * 100, 1) if total_pages > 0 else 0
    }


def batch_create_3up(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    pattern: str = "*.pdf"
) -> List[Dict[str, Any]]:
    """
    Batch converts all PDFs in input_dir into 3-up A4 landscape PDFs in output_dir.
    """
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)

    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    pdf_files = sorted(list(in_dir.glob(pattern)))
    for pdf_path in pdf_files:
        out_name = f"{pdf_path.stem}_3up_a4.pdf"
        out_path = out_dir / out_name
        try:
            res = create_nup_pdf(pdf_path, out_path, pages_per_sheet=3)
            results.append(res)
        except Exception as e:
            results.append({
                "status": "error",
                "input": str(pdf_path),
                "error": str(e)
            })

    return results
