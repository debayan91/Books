"""
3-Up A4 Landscape PDF Converter

Converts any PDF into a new PDF where each A4 landscape page contains 3 original pages 
arranged horizontally (left -> center -> right). Useful for cheap printing.

Requirements:
    pip install pypdf

Usage:
    python make_3up_a4.py

This script will:
1. Read all `.pdf` files inside `input/`
2. Process each file
3. Save the result in `output/` with the suffix `_3up_a4.pdf`
"""

import os
import glob
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

# A4 Size in points (Landscape)
# 1 point = 1/72 inch
A4_WIDTH = 842.0
A4_HEIGHT = 595.0

# Number of pages per sheet horizontally
PAGES_PER_SHEET = 3

def process_pdf(input_path, output_path):
    print(f"Processing {os.path.basename(input_path)} -> {os.path.basename(output_path)}...")
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        num_pages = len(reader.pages)
        if num_pages == 0:
            print(f"Skipping {os.path.basename(input_path)} (0 pages)")
            return
            
        # Divide the width into equal vertical columns 
        # (e.g., 842 / 3 = 280.66 points per column)
        column_width = A4_WIDTH / PAGES_PER_SHEET
        
        # Process pages in chunks of PAGES_PER_SHEET (3)
        for chunk_idx in range(0, num_pages, PAGES_PER_SHEET):
            chunk = reader.pages[chunk_idx : chunk_idx + PAGES_PER_SHEET]
            
            # Create a blank A4 landscape page for the output
            blank_page = PageObject.create_blank_page(width=A4_WIDTH, height=A4_HEIGHT)
            
            for i, page in enumerate(chunk):
                # Calculate scale to fit width or height, maintaining aspect ratio
                orig_width = float(page.mediabox.width)
                orig_height = float(page.mediabox.height)
                
                if orig_width == 0 or orig_height == 0:
                    continue  # Protect against weird pdf pages
                    
                # To maintain aspect ratio, scale should fit within the column width OR the page height
                scale_w = column_width / orig_width
                scale_h = A4_HEIGHT / orig_height
                scale = min(scale_w, scale_h)
                
                scaled_width = orig_width * scale
                scaled_height = orig_height * scale
                
                # Center vertically within the 595 point constraint
                ty = (A4_HEIGHT - scaled_height) / 2.0
                
                # Calculate horizontal translation
                # The regions go from left to right: i=0 is left, i=1 is middle, i=2 is right 
                # Find the starting x-axis position of the column
                column_left_x = i * column_width
                
                # Center horizontally within that specific column slice
                tx = column_left_x + (column_width - scaled_width) / 2.0
                
                # Apply transformation: scale first, then translate
                transform = Transformation().scale(scale, scale).translate(tx, ty)
                
                # We need to apply the transformation to the page before merging
                page.add_transformation(transform)
                
                # Also ensure the media box of the original page doesn't clip the transformed content
                page.mediabox.left = 0
                page.mediabox.bottom = 0
                page.mediabox.right = A4_WIDTH
                page.mediabox.top = A4_HEIGHT
                
                # Merge into our blank page
                blank_page.merge_page(page)
                
            writer.add_page(blank_page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        print(f"  Done. Saved to {output_path}")

    except Exception as e:
        print(f"  Error processing {input_path}: {e}")


def main():
    input_dir = "input"
    output_dir = "output"
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all PDFs in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}/'. Please add some PDFs and run again.")
        return
        
    print(f"Found {len(pdf_files)} PDF(s) to process.")
    
    for pdf_path in pdf_files:
        basename = os.path.basename(pdf_path)
        name, ext = os.path.splitext(basename)
        
        output_name = f"{name}_3up_a4{ext}"
        output_path = os.path.join(output_dir, output_name)
        
        process_pdf(pdf_path, output_path)

if __name__ == "__main__":
    main()
