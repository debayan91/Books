from pypdf import PdfWriter

def merge_pdfs(pdf_paths, output_path):
    """
    Merges multiple PDF files in the specified order and saves the output.
    
    Args:
        pdf_paths (list): List of file paths to the input PDFs, in order.
        output_path (str): File path where the merged PDF should be saved.
    """
    writer = PdfWriter()
    
    for path in pdf_paths:
        writer.append(path)
        
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    writer.close()
