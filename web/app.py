"""
Flask Web Application for PDF Toolkit.
Production-grade REST API and UI routes.
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from werkzeug.utils import secure_filename

import core
from core.config import TEMP_DIR, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS
from core.cleanup import cleanup_temp_files

logger = logging.getLogger("pdf_toolkit.web")


def is_valid_pdf(file_path: Path) -> bool:
    """Verifies that the file starts with the %PDF magic signature."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
            return header.startswith(b"%PDF-")
    except Exception:
        return False


def resolve_uploaded_file(file_id: str) -> Path:
    """Safely resolves an uploaded file id inside TEMP_DIR without path traversal."""
    clean_id = secure_filename(file_id)
    target = TEMP_DIR / clean_id
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"File '{clean_id}' was not found or has expired.")
    return target


def create_app(test_config=None) -> Flask:
    template_folder = str(Path(__file__).resolve().parent / "templates")
    static_folder = str(Path(__file__).resolve().parent / "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )

    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = str(TEMP_DIR)

    if test_config:
        app.config.update(test_config)

    # Initial cleanup of stale temp files on boot
    try:
        cleanup_temp_files()
    except Exception as e:
        logger.warning(f"Initial cleanup error: {e}")

    # --- Error Handlers ---
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "File size exceeds the 200MB limit."}), 413

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error occurred."}), 500

    # --- UI Route ---
    @app.route("/")
    def index():
        return render_template("index.html", version=core.__version__)

    # --- System / Health API ---
    @app.route("/api/health", methods=["GET"])
    def health():
        has_gs = bool(shutil.which("gs") or Path("/opt/homebrew/bin/gs").exists())
        return jsonify({
            "status": "healthy",
            "version": core.__version__,
            "ghostscript_available": has_gs,
            "max_upload_mb": MAX_CONTENT_LENGTH // (1024 * 1024),
            "temp_dir": str(TEMP_DIR)
        })

    # --- Upload API ---
    @app.route("/upload", methods=["POST"])
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded in form data."}), 400

        file = request.files["file"]
        if not file or file.filename == "":
            return jsonify({"error": "No file selected."}), 400

        original_name = file.filename
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Invalid file format. Only PDF files (.pdf) are supported."}), 400

        safe_name = secure_filename(original_name) or "document.pdf"
        file_id = f"{uuid.uuid4().hex}_{safe_name}"
        save_path = TEMP_DIR / file_id

        try:
            file.save(save_path)

            if not is_valid_pdf(save_path):
                save_path.unlink(missing_ok=True)
                return jsonify({"error": "Uploaded file is not a valid PDF (invalid file signature)."}), 400

            file_info = core.get_pdf_info(save_path)
            return jsonify({
                "id": file_id,
                "filename": safe_name,
                "size_bytes": file_info["file_size_bytes"],
                "size_human": file_info["file_size_human"],
                "total_pages": file_info["total_pages"],
                "first_page": file_info["first_page"],
                "message": "File uploaded and verified successfully."
            })
        except Exception as e:
            if save_path.exists():
                save_path.unlink(missing_ok=True)
            return jsonify({"error": f"Failed to process uploaded file: {str(e)}"}), 500

    # --- PDF Info API ---
    @app.route("/info", methods=["POST"])
    @app.route("/api/info", methods=["POST"])
    def get_info():
        data = request.get_json(silent=True) or {}
        file_id = data.get("file")
        if not file_id:
            return jsonify({"error": "Missing 'file' identifier in request payload."}), 400

        try:
            path = resolve_uploaded_file(file_id)
            info = core.get_pdf_info(path)
            return jsonify(info)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Error reading PDF info: {str(e)}"}), 500

    # --- Extract / Split API ---
    @app.route("/extract", methods=["POST"])
    @app.route("/api/extract", methods=["POST"])
    def extract_route():
        data = request.get_json(silent=True) or {}
        file_id = data.get("file")
        ranges_str = data.get("ranges", "").strip()
        mode = data.get("mode", "extract").lower()

        if not file_id:
            return jsonify({"error": "Missing 'file' identifier."}), 400

        try:
            path = resolve_uploaded_file(file_id)
            clean_name = path.stem.split("_", 1)[-1] if "_" in path.stem else path.stem

            if mode == "split":
                out_name = f"split_{uuid.uuid4().hex}.zip"
                out_path = TEMP_DIR / out_name
                core.split_pages(path, out_path, ranges_str, clamp=True)
                download_name = f"Split_{clean_name}.zip"
                mimetype = "application/zip"
            else:
                out_name = f"extracted_{uuid.uuid4().hex}.pdf"
                out_path = TEMP_DIR / out_name
                core.extract_pages(path, out_path, ranges_str, clamp=True)
                download_name = f"Extracted_{clean_name}.pdf"
                mimetype = "application/pdf"

            return send_file(
                str(out_path),
                as_attachment=True,
                download_name=download_name,
                mimetype=mimetype
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

    # --- Merge API ---
    @app.route("/merge", methods=["POST"])
    @app.route("/api/merge", methods=["POST"])
    def merge_route():
        data = request.get_json(silent=True) or {}
        file_ids = data.get("files", [])

        if not file_ids or len(file_ids) < 1:
            return jsonify({"error": "At least one file must be selected for merging."}), 400

        try:
            file_paths = [resolve_uploaded_file(fid) for fid in file_ids]
            out_name = f"merged_{uuid.uuid4().hex}.pdf"
            out_path = TEMP_DIR / out_name

            core.merge_pdfs(file_paths, out_path, add_bookmarks=True)

            return send_file(
                str(out_path),
                as_attachment=True,
                download_name="Merged_Document.pdf",
                mimetype="application/pdf"
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Merge failed: {str(e)}"}), 500

    # --- Extract & Merge API ---
    @app.route("/extract_merge", methods=["POST"])
    @app.route("/api/extract_merge", methods=["POST"])
    def extract_and_merge_route():
        data = request.get_json(silent=True) or {}
        items = data.get("files", [])

        if not items or len(items) < 1:
            return jsonify({"error": "No files provided for extract and merge."}), 400

        try:
            files_data = []
            for it in items:
                fid = it.get("id")
                if not fid:
                    continue
                path = resolve_uploaded_file(fid)
                files_data.append({
                    "path": str(path),
                    "ranges": it.get("ranges", ""),
                    "title": it.get("title")
                })

            out_name = f"extract_merge_{uuid.uuid4().hex}.pdf"
            out_path = TEMP_DIR / out_name

            core.extract_and_merge(files_data, out_path, clamp=True)

            return send_file(
                str(out_path),
                as_attachment=True,
                download_name="Extracted_Merged_Document.pdf",
                mimetype="application/pdf"
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Extract and merge failed: {str(e)}"}), 500

    # --- 3-Up / N-Up Imposition API ---
    @app.route("/api/3up", methods=["POST"])
    def imposition_route():
        data = request.get_json(silent=True) or {}
        file_id = data.get("file")
        pages_per_sheet = int(data.get("cols", 3))
        draw_cut_lines = bool(data.get("cut_lines", False))

        if not file_id:
            return jsonify({"error": "Missing 'file' identifier."}), 400

        try:
            path = resolve_uploaded_file(file_id)
            clean_name = path.stem.split("_", 1)[-1] if "_" in path.stem else path.stem

            out_name = f"3up_{uuid.uuid4().hex}.pdf"
            out_path = TEMP_DIR / out_name

            result = core.create_nup_pdf(
                path,
                out_path,
                pages_per_sheet=pages_per_sheet,
                sheet_size="A4",
                landscape=True,
                draw_cut_lines=draw_cut_lines
            )

            return send_file(
                str(out_path),
                as_attachment=True,
                download_name=f"{clean_name}_{pages_per_sheet}up_a4.pdf",
                mimetype="application/pdf"
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"3-Up imposition failed: {str(e)}"}), 500

    # --- PDF to Word (DOCX) API ---
    @app.route("/api/to_docx", methods=["POST"])
    def to_docx_route():
        data = request.get_json(silent=True) or {}
        file_id = data.get("file")
        start_page = int(data.get("start_page", 0))
        end_page = data.get("end_page")
        end_page = int(end_page) if end_page is not None and str(end_page).isdigit() else None

        if not file_id:
            return jsonify({"error": "Missing 'file' identifier."}), 400

        try:
            path = resolve_uploaded_file(file_id)
            clean_name = path.stem.split("_", 1)[-1] if "_" in path.stem else path.stem

            out_name = f"converted_{uuid.uuid4().hex}.docx"
            out_path = TEMP_DIR / out_name

            core.convert_pdf_to_docx(path, out_path, start_page=start_page, end_page=end_page)

            return send_file(
                str(out_path),
                as_attachment=True,
                download_name=f"{clean_name}.docx",
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Conversion to DOCX failed: {str(e)}"}), 500

    # --- PDF Compression API ---
    @app.route("/compress", methods=["POST"])
    @app.route("/api/compress", methods=["POST"])
    def compress_route():
        data = request.get_json(silent=True) or {}
        file_id = data.get("file")
        level = data.get("level", "medium").lower()

        if not file_id:
            return jsonify({"error": "Missing 'file' identifier."}), 400

        try:
            path = resolve_uploaded_file(file_id)
            clean_name = path.stem.split("_", 1)[-1] if "_" in path.stem else path.stem

            out_name = f"compressed_{uuid.uuid4().hex}.pdf"
            out_path = TEMP_DIR / out_name

            summary = core.compress_pdf(path, out_path, level=level)

            response = send_file(
                str(out_path),
                as_attachment=True,
                download_name=f"Compressed_{clean_name}.pdf",
                mimetype="application/pdf"
            )
            response.headers["X-Original-Size"] = str(summary["original_size_bytes"])
            response.headers["X-Compressed-Size"] = str(summary["compressed_size_bytes"])
            response.headers["X-Reduction-Pct"] = str(summary["reduction_pct"])
            response.headers["Access-Control-Expose-Headers"] = "X-Original-Size, X-Compressed-Size, X-Reduction-Pct"
            return response
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": f"Compression failed: {str(e)}"}), 500

    # --- Temp Cleanup Trigger ---
    @app.route("/api/clean", methods=["POST"])
    def clean_temp_route():
        deleted = cleanup_temp_files(max_age_hours=0.5)
        return jsonify({"message": f"Successfully cleaned up {deleted} temporary items."})

    return app
