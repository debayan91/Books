# PDF Extract and Merge Tool

A modern, localized web application designed to help you quickly reorder and merge multiple PDF documents into a single file securely. 

All processing happens locally on your machine—no cloud uploads involved.

## Features
- **Modern User Interface:** Sleek web app designed with Tailwind CSS
- **Drag & Drop Upload:** Drop native PDFs from your local system right in the browser
- **Dynamic Reordering:** Rearrange PDF merge order by simply dragging file cards
- **Offline Processing:** Merging algorithm runs using local Python engine (via `flask` and `pypdf`)

## Dependencies
- Backend: Python 3.8+, Flask, pypdf
- Frontend: HTML, CSS, JavaScript (Vanilla), Tailwind CSS, SortableJS (for interactions)

## Setup instructions

1. Ensure Python 3.8+ is installed on your machine.
2. Install the necessary packages via `pip`:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the complete application server:
   ```bash
   python main.py
   ```

A lightweight Flask server will instantiate on `localhost:5000` and automatically pop open the viewer in your system's default browser.

To stop the web app server, press `Ctrl+C` in your terminal.
