#!/usr/bin/env python3
"""
PDF Toolkit Pro - Unified System Entry Point.
Single file orchestrator for Web Application, Desktop GUI, and Command-Line Interface.
"""

import os
import sys
import time
import socket
import logging
import argparse
import subprocess
import webbrowser
from pathlib import Path


# =============================================================================
# Python Interpreter Auto-Resolution
# =============================================================================
def ensure_dependencies():
    """
    Checks if required libraries are present. If running in an interpreter
    without packages (e.g. system Python on macOS), attempts to re-exec
    using Python 3.11 or other candidate interpreters where packages are installed.
    """
    try:
        import flask
        import pypdf
        return  # Dependencies found
    except ImportError:
        pass

    candidates = [
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11",
        "/opt/homebrew/bin/python3.11",
        "/usr/local/bin/python3.11",
        "python3.11"
    ]

    for candidate in candidates:
        candidate_path = Path(candidate)
        if candidate_path.exists() or candidate == "python3.11":
            try:
                # Test candidate
                check = subprocess.run(
                    [str(candidate), "-c", "import flask, pypdf"],
                    capture_output=True,
                    text=True
                )
                if check.returncode == 0:
                    # Re-execute seamlessly with candidate
                    os.execv(str(candidate), [str(candidate)] + sys.argv)
            except Exception:
                continue

    # If no candidate worked:
    print("\n[ERROR] Required dependencies are missing from your Python environment.")
    print("Please install them using:")
    print("    pip install -r requirements.txt\n")
    sys.exit(1)


ensure_dependencies()

# Import core modules now that dependencies are verified
import core
from core.config import DEFAULT_HOST, DEFAULT_PORT, TEMP_DIR
from core.cleanup import cleanup_temp_files
from web.app import create_app


# =============================================================================
# Helper: Find Free Port
# =============================================================================
def find_available_port(host: str = "127.0.0.1", start_port: int = 5050, max_attempts: int = 20) -> int:
    """Checks if start_port is available; if not, tests sequential ports."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    # Fallback to system-assigned free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, 0))
        return s.getsockname()[1]


# =============================================================================
# Banner Display
# =============================================================================
def print_banner(host: str, port: int, has_gs: bool):
    url = f"http://{host}:{port}"
    print("=" * 64)
    print("  🚀  PDF TOOLKIT PRO - PRODUCTION SUITE")
    print(f"  Version: {core.__version__} | Mode: Local Offline Processing")
    print("=" * 64)
    print(f"  📍 Web Server Running at: \033[1;36m{url}\033[0m")
    print(f"  📁 Temp Storage:         {TEMP_DIR}")
    print(f"  ⚙️  Ghostscript:          {'Enabled (/opt/homebrew/bin/gs)' if has_gs else 'PyPDF Lossless Fallback'}")
    print("=" * 64)
    print("  Available Tools in Web Suite:")
    print("    1. Extract & Split (Single PDF or ZIP)")
    print("    2. Multi-PDF Merge (Drag-and-drop reorder)")
    print("    3. Extract & Merge (Custom page ranges per document)")
    print("    4. 3-Up Print Prep (A4 Landscape Imposition for books)")
    print("    5. PDF to Microsoft Word (.docx conversion)")
    print("    6. PDF Compression & Optimizer")
    print("    7. PDF Inspector & Dimensions Analyzer")
    print("=" * 64)
    print("  Press Ctrl+C to safely shutdown.\n")


# =============================================================================
# Web Server Runner
# =============================================================================
def run_web(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, open_browser: bool = True):
    final_port = find_available_port(host, port)
    if final_port != port:
        print(f"[NOTE] Port {port} was occupied (e.g. AirPlay). Switched to free port {final_port}.")

    app = create_app()

    has_gs = bool(os.path.exists("/opt/homebrew/bin/gs") or os.system("which gs > /dev/null 2>&1") == 0)
    print_banner(host, final_port, has_gs)

    if open_browser:
        target_url = f"http://{host}:{final_port}"
        import threading
        def _open():
            time.sleep(1.0)
            webbrowser.open(target_url)
        threading.Thread(target=_open, daemon=True).start()

    # Disable werkzeug development banner for production cleanliness
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    try:
        app.run(host=host, port=final_port, threaded=True, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n[INFO] Gracefully shutting down PDF Toolkit server...")
        cleanup_temp_files(max_age_hours=0.1)
        sys.exit(0)


# =============================================================================
# Desktop GUI Runner
# =============================================================================
def run_gui():
    print("[INFO] Launching PDF Toolkit Pro Desktop GUI...")
    from gui import run_app
    run_app()


# =============================================================================
# CLI Subcommands
# =============================================================================
def cli_merge(args):
    out = args.output or "merged_output.pdf"
    res = core.merge_pdfs(args.files, out)
    print(f"[SUCCESS] Merged {res['files_merged']} files ({res['total_pages']} pages) into: {out}")


def cli_extract(args):
    out = args.output or f"{Path(args.input).stem}_extracted.pdf"
    res = core.extract_pages(args.input, out, args.ranges or "")
    print(f"[SUCCESS] Extracted {res['pages_extracted']} pages into: {out}")


def cli_split(args):
    out = args.output or f"{Path(args.input).stem}_split.zip"
    res = core.split_pages(args.input, out, args.ranges or "")
    print(f"[SUCCESS] Split document into {res['parts_count']} parts in archive: {out}")


def cli_3up(args):
    if args.batch:
        in_dir = args.input or "input"
        out_dir = args.output or "output"
        print(f"[INFO] Batch converting PDFs from '{in_dir}' to 3-Up in '{out_dir}'...")
        results = core.batch_create_3up(in_dir, out_dir)
        print(f"[SUCCESS] Processed {len(results)} file(s).")
    else:
        if not args.input:
            print("[ERROR] Input file is required. Example: python start.py 3up input.pdf -o output.pdf")
            sys.exit(1)
        cols = args.cols or 3
        out = args.output or f"{Path(args.input).stem}_{cols}up_a4.pdf"
        res = core.create_nup_pdf(args.input, out, pages_per_sheet=cols)
        print(f"[SUCCESS] Created {cols}-Up imposition: {res['original_pages']} pages -> {res['output_sheets']} sheets ({res['paper_savings_pct']}% paper saved).")
        print(f"          Output: {out}")


def cli_docx(args):
    out = args.output or f"{Path(args.input).stem}.docx"
    print(f"[INFO] Converting '{args.input}' to Word document...")
    res = core.convert_pdf_to_docx(args.input, out)
    print(f"[SUCCESS] Converted in {res['duration_seconds']}s. Output: {out}")


def cli_compress(args):
    out = args.output or f"{Path(args.input).stem}_compressed.pdf"
    level = args.level or "medium"
    print(f"[INFO] Compressing '{args.input}' with preset '{level}'...")
    res = core.compress_pdf(args.input, out, level=level)
    print(f"[SUCCESS] Compressed via {res['method']}! Original: {res['original_size_human']} -> Compressed: {res['compressed_size_human']} ({res['reduction_pct']}% reduction).")
    print(f"          Output: {out}")


def cli_info(args):
    info = core.get_pdf_info(args.input)
    print("\n" + "=" * 50)
    print(f"  PDF Document: {info['filename']}")
    print("=" * 50)
    print(f"  Pages:        {info['total_pages']}")
    print(f"  File Size:    {info['file_size_human']}")
    print(f"  Encrypted:    {'Yes' if info['is_encrypted'] else 'No'}")
    if info["first_page"]:
        fp = info["first_page"]
        print(f"  Dimensions:   {fp['width_mm']} x {fp['height_mm']} mm ({fp['paper_size']})")
        print(f"  Orientation:  {fp['orientation']}")
    print(f"  Title:        {info['title']}")
    print(f"  Author:       {info['author']}")
    print(f"  Producer:     {info['producer']}")
    print("=" * 50 + "\n")


def cli_clean(args):
    count = cleanup_temp_files(max_age_hours=0.0)
    print(f"[SUCCESS] Cleaned {count} items from temporary storage.")


def cli_test(args):
    print("[INFO] Running PDF Toolkit Automated Test Suite...")
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-t", ".", "-s", "tests", "-v"])
    sys.exit(res.returncode)


# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="PDF Toolkit Pro - Production-grade Local PDF Suite.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--gui", action="store_true", help="Launch the Desktop GUI application.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Web server port (default: {DEFAULT_PORT}).")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help=f"Web server host (default: {DEFAULT_HOST}).")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser.")

    subparsers = parser.add_subparsers(dest="command", help="Command-line utilities")

    # Merge
    p_merge = subparsers.add_parser("merge", help="Merge multiple PDF files.")
    p_merge.add_argument("files", nargs="+", help="Input PDF files.")
    p_merge.add_argument("-o", "--output", help="Output PDF file path.")
    p_merge.set_defaults(func=cli_merge)

    # Extract
    p_extract = subparsers.add_parser("extract", help="Extract page ranges from PDF.")
    p_extract.add_argument("input", help="Source PDF file.")
    p_extract.add_argument("-r", "--ranges", help="Page ranges (e.g. '1-5, 8').")
    p_extract.add_argument("-o", "--output", help="Output PDF file path.")
    p_extract.set_defaults(func=cli_extract)

    # Split
    p_split = subparsers.add_parser("split", help="Split PDF into ZIP archive.")
    p_split.add_argument("input", help="Source PDF file.")
    p_split.add_argument("-r", "--ranges", help="Ranges to split, or leave blank for all pages.")
    p_split.add_argument("-o", "--output", help="Output ZIP file path.")
    p_split.set_defaults(func=cli_split)

    # 3-Up
    p_3up = subparsers.add_parser("3up", help="Convert PDF into 3-Up A4 landscape sheets.")
    p_3up.add_argument("input", nargs="?", help="Source PDF file or directory.")
    p_3up.add_argument("-o", "--output", help="Output PDF file or directory.")
    p_3up.add_argument("--cols", type=int, default=3, help="Pages per sheet (2, 3, or 4). Default: 3.")
    p_3up.add_argument("--batch", action="store_true", help="Batch process all PDFs in directory.")
    p_3up.set_defaults(func=cli_3up)

    # DOCX
    p_docx = subparsers.add_parser("to-docx", help="Convert PDF to Word (.docx).")
    p_docx.add_argument("input", help="Source PDF file.")
    p_docx.add_argument("-o", "--output", help="Output .docx file path.")
    p_docx.set_defaults(func=cli_docx)

    # Compress
    p_comp = subparsers.add_parser("compress", help="Compress PDF with Ghostscript or PyPDF.")
    p_comp.add_argument("input", help="Source PDF file.")
    p_comp.add_argument("-o", "--output", help="Output PDF file path.")
    p_comp.add_argument("-l", "--level", choices=["low", "medium", "high"], default="medium", help="Preset.")
    p_comp.set_defaults(func=cli_compress)

    # Info
    p_info = subparsers.add_parser("info", help="Inspect PDF properties and metadata.")
    p_info.add_argument("input", help="PDF file to inspect.")
    p_info.set_defaults(func=cli_info)

    # Clean
    p_clean = subparsers.add_parser("clean", help="Clean up temporary files.")
    p_clean.set_defaults(func=cli_clean)

    # Test
    p_test = subparsers.add_parser("test", help="Run automated test suite.")
    p_test.set_defaults(func=cli_test)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    elif args.gui:
        run_gui()
    else:
        # Default action: run the production web server
        run_web(host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
