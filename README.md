# PDF Toolkit

A collection of lightweight, local PDF utilities for macOS.

## Tools

### 1. PDF Range Extractor (Desktop Utility)

A simple Tkinter-based application to extract specific page ranges from a PDF.

- **Features**: Drag and drop, page range parsing (`1-5, 8`), validation, and automatic naming.
- **Entry Point**: `python main.py`

### 2. PDF Merge Tool (Local Web App)

A modern, monochrome web interface for merging multiple PDF files.

- **Features**:
  - **Premium Monochrome Design**: Sleek black and white UI with high-contrast elements.
  - **Drag-and-Drop Reordering**: Use SortableJS to arrange files before merging.
  - **Local Processing**: No cloud dependencies, everything stays on your machine.
- **Entry Point**: `python pdf_extractor/server.py`

---

## Installation

1. Ensure you have Python 3.10+ installed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   *Note: For the desktop app, `tkinterdnd2` is required. For the web app, `flask` is required.*

## Usage

### Using the Desktop Extractor

1. Run: `python main.py`
2. Drag a PDF into the window.
3. Enter ranges (e.g., `1-3, 7`) and click "Create New PDF".

### Using the Web Merge Tool

1. Run: `python pdf_extractor/server.py`
2. Open your browser to `http://127.0.0.1:5000`.
3. Drag files into the drop zone, reorder them, and click "Merge PDFs".

## Project Structure

- `main.py`: Entry point for the desktop app.
- `pdf_extractor/server.py`: Entry point for the web merge tool.
- `pdf_extractor/static/`: CSS (monochrome) and JS (SortableJS) for the web UI.
- `pdf_extractor/templates/`: HTML templates for the web UI.
- `gui.py`: Tkinter GUI logic.
- `pdf_utils.py`: Shared PDF processing logic (extraction and merging).
- `.gitignore`: Configured to ignore `input/`, `output/`, and `ready to print/` folders.

## Development Note

The web UI recently underwent a design overhaul to implement a **strictly monochrome (B&W) theme**, providing a high-contrast, professional aesthetic.
