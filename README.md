# PDF Range Extractor

A small, extremely simple macOS desktop application that extracts specific page ranges from a PDF and saves them into a new PDF. 

## Description
This tiny utility allows you to drag a PDF file into the window, specify exactly which pages you want to keep, and save a new PDF containing only those pages. It handles both single pages and ranges, maintaining the exact order you provide.

## Features
- **Drag and Drop Interface**: Easily load PDFs by dragging them into the application.
- **Support for Page Ranges**: Handles formats like `1-5, 8, 10-12`.
- **Validation**: Automatically checks page numbers against the total length of the document.
- **Automatic Naming**: Suggests a filename like `originalname_extracted.pdf`.
- **Standalone Layout**: Simple, vertical UI for quick operation.

## Installation
1. Ensure you have Python 3.10 or higher installed on your macOS.
2. Clone or download this repository to your local machine.
3. Open your terminal and navigate to the project folder.
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application using Python:
   ```bash
   python main.py
   ```
2. **Drag a PDF file** into the designated gray area within the window.
3. Enter your desired **Page Ranges** in the text field.
   - Example: `1-5,8,10-12`
   - This will extract pages 1 through 5, page 8, and pages 10 through 12.
4. Click the **Create New PDF** button.
5. Choose where to save your new PDF file.
6. Check the **Status** area for success messages or error reports.

## Project Structure
- `main.py`: Entry point for the application.
- `gui.py`: Contains all GUI logic and window layout.
- `pdf_utils.py`: Contains the page range parser and PDF extraction logic.
- `requirements.txt`: List of Python dependencies.
- `.gitignore`: Files to exclude from Git.
- `README.md`: This file.
