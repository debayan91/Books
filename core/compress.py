"""
PDF Compression & Optimization Module.
Supports Ghostscript (high-ratio resampling) with automatic PyPDF fallback.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Union, Dict, Any
from pypdf import PdfReader, PdfWriter
from core.info import format_file_size

GS_PRESETS = {
    "low": "/screen",      # 72 dpi - Smallest size
    "medium": "/ebook",    # 150 dpi - Balanced quality & size
    "high": "/printer",    # 300 dpi - Crisp prints
    "prepress": "/prepress"# High fidelity color preservation
}


def compress_with_ghostscript(
    input_path: Path,
    output_path: Path,
    level: str = "medium"
) -> bool:
    """Runs Ghostscript pdfwrite to compress."""
    gs_bin = shutil.which("gs") or "/opt/homebrew/bin/gs" or "/usr/local/bin/gs"
    if not Path(gs_bin).exists() and not shutil.which("gs"):
        return False

    gs_preset = GS_PRESETS.get(level.lower(), "/ebook")
    cmd = [
        str(gs_bin),
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_preset}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path)
    ]

    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path.exists() and output_path.stat().st_size > 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def compress_with_pypdf(input_path: Path, output_path: Path) -> None:
    """PyPDF lossless stream and object compression fallback."""
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()


def compress_pdf(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    level: str = "medium"
) -> Dict[str, Any]:
    """
    Compresses a PDF file using the best available engine.
    """
    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input file not found: {in_p}")

    out_p.parent.mkdir(parents=True, exist_ok=True)
    orig_size = in_p.stat().st_size

    method_used = "ghostscript"
    success = compress_with_ghostscript(in_p, out_p, level=level)

    if not success:
        # Fallback to PyPDF
        method_used = "pypdf_lossless"
        compress_with_pypdf(in_p, out_p)

    compressed_size = out_p.stat().st_size if out_p.exists() else orig_size
    saved_bytes = max(0, orig_size - compressed_size)
    savings_pct = round((saved_bytes / orig_size) * 100, 1) if orig_size > 0 else 0

    return {
        "status": "success",
        "input": str(in_p),
        "output": str(out_p),
        "method": method_used,
        "compression_level": level,
        "original_size_bytes": orig_size,
        "compressed_size_bytes": compressed_size,
        "original_size_human": format_file_size(orig_size),
        "compressed_size_human": format_file_size(compressed_size),
        "saved_bytes": saved_bytes,
        "saved_bytes_human": format_file_size(saved_bytes),
        "reduction_pct": savings_pct
    }
