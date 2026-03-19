import os
import zipfile
import subprocess
from pypdf import PdfWriter, PdfReader

def parse_ranges(ranges_str, total_pages):
    """
    Parses a string of page ranges (e.g., '1-5,8,10-12') into a list of 0-based page indices.
    Returns all pages if ranges_str is empty.
    """
    if not ranges_str or not ranges_str.strip():
        # If empty, return all pages
        return list(range(total_pages))
        
    pages = []
    parts = [p.strip() for p in ranges_str.split(',')]
    for part in parts:
        if not part: 
            continue
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            start = int(start_str.strip()) if start_str.strip() else 1
            end = int(end_str.strip()) if end_str.strip() else total_pages
            
            # Constrain to 1-based bounds
            start = max(1, min(start, total_pages))
            end = max(1, min(end, total_pages))
            
            if start <= end:
                pages.extend(range(start - 1, end))
        else:
            page = int(part)
            if 1 <= page <= total_pages:
                pages.append(page - 1)
                
    # Remove duplicates but preserve order
    return list(dict.fromkeys(pages))

def merge_pdfs(pdf_paths, output_path):
    """
    Merges multiple PDF files in the specified order and saves the output.
    """
    writer = PdfWriter()
    
    for path in pdf_paths:
        writer.append(path)
        
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()

def extract_pages(pdf_path, ranges_str, output_path):
    """
    Extracts specific pages from a single PDF and saves to output_path.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    pages_to_extract = parse_ranges(ranges_str, total_pages)
    
    writer = PdfWriter()
    for p_num in pages_to_extract:
        writer.add_page(reader.pages[p_num])
        
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()

def extract_and_merge(files_data, output_path):
    """
    Extracts pages from multiple PDFs and merges them in order.
    files_data is a list of dicts: [{'path': '/path/to/pdf', 'ranges': '1-5'}, ...]
    """
    writer = PdfWriter()
    
    for item in files_data:
        path = item['path']
        ranges_str = item.get('ranges', '')
        
        reader = PdfReader(path)
        total_pages = len(reader.pages)
        pages_to_extract = parse_ranges(ranges_str, total_pages)
        
        for p_num in pages_to_extract:
            writer.add_page(reader.pages[p_num])
            
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()

def split_pages(pdf_path, ranges_str, output_zip_path):
    """
    Extracts each range separately and saves them into a ZIP file.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    parts = [p.strip() for p in ranges_str.split(',') if p.strip()]
    if not parts:
        parts = [f"1-{total_pages}"]
        
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for i, part in enumerate(parts):
            pages_to_extract = parse_ranges(part, total_pages)
            if not pages_to_extract:
                continue
                
            writer = PdfWriter()
            for p_num in pages_to_extract:
                writer.add_page(reader.pages[p_num])
                
            temp_pdf_name = f"part_{i+1}_{part.replace(' ', '')}.pdf"
            temp_pdf_path = os.path.join(os.path.dirname(output_zip_path), temp_pdf_name)
            with open(temp_pdf_path, "wb") as output_file:
                writer.write(output_file)
            writer.close()
            
            zipf.write(temp_pdf_path, temp_pdf_name)
            os.remove(temp_pdf_path)

def compress_pdf(input_path, output_path, level):
    """
    Compresses a PDF using Ghostscript based on the specified level.
    """
    gs_settings = {
        'low': '/screen',
        'medium': '/ebook',
        'high': '/printer'
    }
    setting = gs_settings.get(level, '/screen')
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={setting}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
        f'-sOutputFile={output_path}', input_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise Exception("Ghostscript is not installed on this system.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Compression failed: {e.stderr.decode('utf-8')}")
