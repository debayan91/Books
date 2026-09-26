# PDF Toolkit Pro

A production-grade, privacy-first local PDF manipulation, imposition, and conversion suite for macOS and Linux.

Every operation runs 100% locally on your machine—no cloud uploads, no subscriptions, zero telemetry.

---

## ⚡ Quick Start

Run the entire system with a single command:

```bash
python3 start.py
```

`start.py` will:
1. Verify the Python environment and automatically re-resolve to an interpreter with installed dependencies if needed.
2. Select an available network port (automatically bypassing macOS AirPlay on port 5000).
3. Start the local server and open your default browser to the web suite.

---

## 🌟 Capabilities

| Tool | Description | Web | Desktop GUI | CLI |
| :--- | :--- | :---: | :---: | :---: |
| **Extract & Split** | Extract page ranges (`1-5, 8`) to a single PDF or split into a ZIP archive | ✅ | ✅ | ✅ |
| **Merge PDFs** | Combine multiple documents with drag-and-drop reordering and outline bookmarks | ✅ | ✅ | ✅ |
| **Extract & Merge** | Extract custom page ranges per document and merge in one continuous operation | ✅ | ❌ | ✅ |
| **3-Up Print Prep** | Convert PDFs into A4 landscape sheets (2-up, 3-up, 4-up) for ~66.7% paper savings | ✅ | ✅ | ✅ |
| **PDF to Word** | Convert documents to editable Microsoft Word files (`.docx`) | ✅ | ✅ | ✅ |
| **Compress PDF** | Reduce file size via Ghostscript resampling or PyPDF lossless stream compression | ✅ | ❌ | ✅ |
| **PDF Inspector** | Inspect physical dimensions (mm/pt), paper format (A4/Letter), encryption, metadata | ✅ | ✅ | ✅ |

---

## 🖥️ Usage Modes

### 1. Unified Web Application (Default)

Launch the web application:
```bash
python3 start.py
```

Options:
```bash
python3 start.py --port 8080      # Custom port
python3 start.py --host 0.0.0.0   # Allow LAN access
python3 start.py --no-browser     # Headless server mode
```

### 2. Desktop GUI (Tkinter)

Launch the native desktop interface:
```bash
python3 start.py --gui
```
*(Or run `python3 gui.py` directly)*

### 3. Command-Line Interface (CLI)

The `start.py` entry point provides full CLI subcommands for automation and scripting:

#### Merge Documents
```bash
python3 start.py merge doc1.pdf doc2.pdf doc3.pdf -o merged.pdf
```

#### Extract Page Ranges
```bash
python3 start.py extract sample.pdf -r "1-5, 8, 10-12" -o extracted.pdf
```

#### Split into ZIP
```bash
python3 start.py split sample.pdf -r "1-5, 6-10" -o split_parts.zip
# Split every page into separate files:
python3 start.py split sample.pdf -o all_pages.zip
```

#### 3-Up / N-Up Imposition (Booklet Print Layout)
```bash
# Single file:
python3 start.py 3up book.pdf -o book_3up_a4.pdf --cols 3

# Batch process entire directory:
python3 start.py 3up --batch input/ -o output/
```

#### Convert PDF to Word (.docx)
```bash
python3 start.py to-docx document.pdf -o document.docx
```

#### Compress / Optimize PDF
```bash
# Levels: low (72 dpi), medium (150 dpi, default), high (300 dpi)
python3 start.py compress large.pdf -o compressed.pdf --level medium
```

#### Inspect Metadata & Physical Properties
```bash
python3 start.py info document.pdf
```

#### Temporary Storage Cleanup
```bash
python3 start.py clean
```

#### Run Automated Test Suite
```bash
python3 start.py test
```

---

## 📁 Project Architecture

```
books/
├── start.py                # 🚀 Unified System Entry Point (Web, GUI, CLI)
├── main.py                 # Legacy compatibility wrapper -> start.py
├── make_3up_a4.py          # Legacy compatibility wrapper for 3-Up imposition
├── pdf_to_docx.py          # Legacy compatibility wrapper for Word conversion
├── pdf_utils.py            # Legacy compatibility wrapper for core engine
├── requirements.txt        # Production dependencies
│
├── core/                   # 🧠 Production-Grade Engine
│   ├── __init__.py         # Public library API exports
│   ├── config.py           # Paths, ports, and limits
│   ├── extract.py          # Range parser, single extract, ZIP split
│   ├── merge.py            # Multi-PDF merge and extract-and-merge
│   ├── imposition.py       # N-Up layout engine (3-up A4 landscape)
│   ├── convert.py          # PDF to DOCX converter
│   ├── compress.py         # Ghostscript & PyPDF compression
│   ├── info.py             # Dimensions and metadata inspector
│   └── cleanup.py          # TTL temporary file cleanup manager
│
├── web/                    # 🌐 Modern Web Application
│   ├── __init__.py         # App factory
│   ├── app.py              # REST API & routes
│   ├── static/
│   │   ├── css/app.css     # Production design system (Dark & Light theme)
│   │   └── js/app.js       # Interactive frontend (drag-drop, SortableJS, toasts)
│   └── templates/
│       └── index.html      # Responsive web UI
│
├── gui.py                  # 🖥️ Desktop Multi-Tool GUI (Tkinter + TkinterDnD)
│
└── tests/                  # 🧪 Comprehensive Test Suite (100% pass)
    ├── helpers.py          # Synthetic PDF generator
    ├── test_ranges.py      # Range syntax unit tests
    ├── test_core.py        # Core engine integration tests
    └── test_api.py         # Flask REST API endpoint tests
```

---

## 🔧 Installation & Dependencies

Ensure Python 3.10+ is installed on your machine.

```bash
pip install -r requirements.txt
```

### Optional External Tools
- **Ghostscript** (`gs`): Used for high-ratio image resampling during compression. If not present, the tool automatically falls back to PyPDF lossless stream and object deduplication.
  - Install on macOS via Homebrew: `brew install ghostscript`

---

## 🧪 Testing

Run the test suite:

```bash
python3 start.py test
```

All 29 tests cover range parsing, page extraction, ZIP splitting, bookmark merging, 3-up A4 imposition geometry, DOCX conversion, compression fallbacks, and REST API routes.

---

## 🔒 Security & Privacy

- **100% Local**: Files never leave your local machine or network.
- **Header Verification**: Uploaded files are validated against the `%PDF-` magic byte signature.
- **Path Traversal Protection**: All temporary IDs are sanitized via `secure_filename`.
- **Automatic Storage Cleanup**: Temporary staging files in `.temp_storage` are subject to automated TTL garbage collection.
