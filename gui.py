import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import pdf_utils

class PDFExtractorApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("PDF Range Extractor")
        self.geometry("400x400")
        self.configure(padx=20, pady=20)
        self.resizable(False, False)
        
        self.current_pdf_path = None
        self.total_pages = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        # 1. Drag and Drop Zone
        self.drop_frame = tk.Frame(self, bg="#e0e0e0", width=360, height=120, bd=2, relief="groove")
        self.drop_frame.pack_propagate(False)
        self.drop_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.drop_label = tk.Label(self.drop_frame, text="Drag PDF Here", bg="#e0e0e0", font=("Helvetica", 16))
        self.drop_label.pack(expand=True)
        
        # Register drop target
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # 2. File Info
        self.file_info_frame = tk.Frame(self)
        self.file_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.filename_label = tk.Label(self.file_info_frame, text="Loaded File: None", anchor="w", font=("Helvetica", 12))
        self.filename_label.pack(fill=tk.X)
        
        self.pages_label = tk.Label(self.file_info_frame, text="Total Pages: -", anchor="w", font=("Helvetica", 12))
        self.pages_label.pack(fill=tk.X)
        
        # 3. Page Range Input
        self.range_frame = tk.Frame(self)
        self.range_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(self.range_frame, text="Page Ranges (e.g., 1-5,8,10-12):", anchor="w", font=("Helvetica", 12)).pack(fill=tk.X)
        self.range_entry = tk.Entry(self.range_frame, font=("Helvetica", 12))
        self.range_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 4. Create Button
        self.create_btn = tk.Button(self, text="Create New PDF", command=self.create_pdf, state=tk.DISABLED, font=("Helvetica", 12, "bold"))
        self.create_btn.pack(pady=(0, 15))
        
        # 5. Status Messages
        self.status_label = tk.Label(self, text="Status: Ready", fg="blue", wraplength=360, font=("Helvetica", 11))
        self.status_label.pack(fill=tk.BOTH, expand=True)

    def set_status(self, message, is_error=False):
        color = "red" if is_error else "green"
        if message == "Ready":
            color = "blue"
        self.status_label.config(text=f"Status: {message}", fg=color)

    def on_drop(self, event):
        # Extract the path dropped from Event Data
        files = self.tk.splitlist(event.data)
        if not files:
            return
            
        file_path = files[0]
        
        # Strip potential file:// prefix (common in macOS depending on the source)
        if file_path.startswith("file://"):
            file_path = file_path[7:]
            
        if not file_path.lower().endswith(".pdf"):
            self.set_status("Please drop a valid PDF file.", is_error=True)
            return
            
        self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            self.total_pages = pdf_utils.get_pdf_info(file_path)
            self.current_pdf_path = file_path
            
            filename = os.path.basename(file_path)
            self.filename_label.config(text=f"Loaded File: {filename}")
            self.pages_label.config(text=f"Total Pages: {self.total_pages}")
            
            self.create_btn.config(state=tk.NORMAL)
            self.set_status(f"Loaded {filename} successfully.")
        except Exception as e:
            self.set_status(f"Error loading PDF: {str(e)}", is_error=True)
            self.current_pdf_path = None
            self.total_pages = 0
            self.filename_label.config(text="Loaded File: None")
            self.pages_label.config(text="Total Pages: -")
            self.create_btn.config(state=tk.DISABLED)

    def create_pdf(self):
        if not self.current_pdf_path:
            self.set_status("No PDF loaded.", is_error=True)
            return
            
        range_text = self.range_entry.get().strip()
        if not range_text:
            self.set_status("Please enter page ranges.", is_error=True)
            return
            
        try:
            pages_to_extract = pdf_utils.parse_page_ranges(range_text, self.total_pages)
        except ValueError as e:
            self.set_status(str(e), is_error=True)
            return
            
        if not pages_to_extract:
            self.set_status("No pages to extract.", is_error=True)
            return

        # Bonus: automatically suggest output filename `originalname_extracted.pdf`
        orig_dir = os.path.dirname(self.current_pdf_path)
        orig_name = os.path.basename(self.current_pdf_path)
        name_root, ext = os.path.splitext(orig_name)
        suggested_name = f"{name_root}_extracted{ext}"
        
        save_path = filedialog.asksaveasfilename(
            initialdir=orig_dir,
            initialfile=suggested_name,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not save_path:
            self.set_status("Save cancelled.")  # No error, just standard info
            return
            
        try:
            pdf_utils.extract_pages(self.current_pdf_path, save_path, pages_to_extract)
            self.set_status(f"Successfully saved {os.path.basename(save_path)}")
        except Exception as e:
            self.set_status(f"Error saving PDF: {str(e)}", is_error=True)

def run_app():
    app = PDFExtractorApp()
    app.mainloop()
