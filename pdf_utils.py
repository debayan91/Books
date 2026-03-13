import os
from pypdf import PdfReader, PdfWriter

def parse_page_ranges(range_str, max_pages):
    """
    Parses a page range string like '1-5,8,10-12' and returns a list of 0-indexed page numbers.
    Validates against max_pages.
    """
    range_str = range_str.replace(" ", "")
    if not range_str:
        return []
        
    pages = []
    parts = range_str.split(",")
    for part in parts:
        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str)
                end = int(end_str)
            except ValueError:
                raise ValueError(f"Invalid range format: {part}")
                
            if start > end:
                raise ValueError(f"Start page greater than end page: {part}")
            if start < 1 or end > max_pages:
                raise ValueError(f"Page range out of bounds: {part} (max: {max_pages})")
                
            pages.extend(range(start, end + 1))
        else:
            try:
                page = int(part)
            except ValueError:
                raise ValueError(f"Invalid page number format: {part}")
                
            if page < 1 or page > max_pages:
                raise ValueError(f"Page number out of bounds: {part} (max: {max_pages})")
            pages.append(page)
            
    return [p - 1 for p in pages]


def get_pdf_info(filepath):
    """Returns the number of pages in the PDF."""
    try:
        reader = PdfReader(filepath)
        return len(reader.pages)
    except Exception as e:
        raise ValueError(f"Could not read PDF: {str(e)}")


def extract_pages(input_path, output_path, pages_0_indexed):
    """Extracts specified 0-indexed pages from input_path and saves to output_path."""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for p in pages_0_indexed:
            writer.add_page(reader.pages[p])
            
        with open(output_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        raise ValueError(f"Error during extraction: {str(e)}")
