"""
Desktop GUI Utility for PDF Toolkit.
Modernized multi-tool interface with drag-and-drop and fallback file pickers.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Attempt to load TkinterDnD for drag and drop; fallback gracefully if unavailable
HAS_DND = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
    BaseTkClass = TkinterDnD.Tk
except Exception:
    BaseTkClass = tk.Tk

import core


class PDFToolkitApp(BaseTkClass):
    def __init__(self):
        super().__init__()

        self.title("PDF Toolkit Pro - Desktop Edition")
        self.geometry("640x520")
        self.minsize(560, 460)

        # Style configuration
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.create_extract_tab()
        self.create_merge_tab()
        self.create_3up_tab()
        self.create_docx_tab()

        # Global Status Bar
        self.status_var = tk.StringVar(value="Ready. 100% offline & local processing.")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=(8, 4))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def set_status(self, message: str):
        self.status_var.set(message)
        self.update_idletasks()

    # -------------------------------------------------------------------------
    # TAB 1: RANGE EXTRACTOR
    # -------------------------------------------------------------------------
    def create_extract_tab(self):
        frame = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(frame, text="Extract & Split")

        self.extract_path_var = tk.StringVar()
        self.extract_info_var = tk.StringVar(value="No file loaded")

        # File selection frame
        f_frame = ttk.LabelFrame(frame, text="Source PDF Document", padding=12)
        f_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Entry(f_frame, textvariable=self.extract_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(f_frame, text="Browse...", command=self.browse_extract_file).pack(side=tk.RIGHT)

        ttk.Label(f_frame, textvariable=self.extract_info_var, font=("Helvetica", 10, "italic")).pack(fill=tk.X, pady=(6, 0))

        # Range Options Frame
        r_frame = ttk.LabelFrame(frame, text="Extraction Configuration", padding=12)
        r_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(r_frame, text="Page Ranges (e.g. 1-5, 8, 10-12):").pack(anchor="w")
        self.extract_range_entry = ttk.Entry(r_frame)
        self.extract_range_entry.pack(fill=tk.X, pady=(4, 8))

        self.extract_mode_var = tk.StringVar(value="extract")
        ttk.Radiobutton(r_frame, text="Single Extracted PDF", variable=self.extract_mode_var, value="extract").pack(anchor="w")
        ttk.Radiobutton(r_frame, text="Split into ZIP of separate PDFs", variable=self.extract_mode_var, value="split").pack(anchor="w")

        # Action Button
        self.btn_run_extract = ttk.Button(frame, text="Extract Pages", command=self.run_extract_threaded)
        self.btn_run_extract.pack(pady=10)

    def browse_extract_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.load_extract_pdf(filename)

    def load_extract_pdf(self, path: str):
        try:
            info = core.get_pdf_info(path)
            self.extract_path_var.set(path)
            self.extract_info_var.set(f"Loaded: {info['filename']} | {info['total_pages']} pages | {info['file_size_human']}")
            self.set_status(f"Loaded {info['filename']}")
        except Exception as e:
            messagebox.showerror("Error Loading PDF", str(e))

    def run_extract_threaded(self):
        src = self.extract_path_var.get()
        if not src:
            messagebox.showwarning("Missing Input", "Please select a PDF file first.")
            return

        ranges = self.extract_range_entry.get().strip()
        mode = self.extract_mode_var.value if hasattr(self.extract_mode_var, "value") else self.extract_mode_var.get()

        out_ext = ".zip" if mode == "split" else ".pdf"
        default_name = f"{Path(src).stem}_extracted{out_ext}"

        save_path = filedialog.asksaveasfilename(
            defaultextension=out_ext,
            initialfile=default_name,
            filetypes=[("Archive", "*.zip")] if mode == "split" else [("PDF files", "*.pdf")]
        )
        if not save_path:
            return

        self.btn_run_extract.config(state="disabled")
        self.set_status("Extracting pages in background...")

        def worker():
            try:
                if mode == "split":
                    core.split_pages(src, save_path, ranges, clamp=True)
                else:
                    core.extract_pages(src, save_path, ranges, clamp=True)
                self.after(0, lambda: messagebox.showinfo("Success", f"Extraction completed!\nSaved to: {save_path}"))
                self.after(0, lambda: self.set_status("Extraction completed successfully."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Extraction Error", str(e)))
                self.after(0, lambda: self.set_status(f"Error: {e}"))
            finally:
                self.after(0, lambda: self.btn_run_extract.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # TAB 2: PDF MERGER
    # -------------------------------------------------------------------------
    def create_merge_tab(self):
        frame = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(frame, text="Merge PDFs")

        top_bar = ttk.Frame(frame)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(top_bar, text="Add PDF Files...", command=self.add_merge_files).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top_bar, text="Move Up", command=self.move_merge_up).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Move Down", command=self.move_merge_down).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Remove", command=self.remove_merge_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Clear All", command=self.clear_merge_files).pack(side=tk.RIGHT)

        # File Listbox
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.merge_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Helvetica", 11))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.merge_listbox.yview)
        self.merge_listbox.configure(yscrollcommand=scrollbar.set)

        self.merge_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.merge_files_data = []

        self.btn_run_merge = ttk.Button(frame, text="Merge All Files", command=self.run_merge_threaded)
        self.btn_run_merge.pack(pady=10)

    def add_merge_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for f in files:
            if f not in self.merge_files_data:
                self.merge_files_data.append(f)
                self.merge_listbox.insert(tk.END, Path(f).name)
        self.set_status(f"{len(self.merge_files_data)} files in merge sequence.")

    def remove_merge_file(self):
        sel = self.merge_listbox.curselection()
        if sel:
            idx = sel[0]
            self.merge_listbox.delete(idx)
            self.merge_files_data.pop(idx)

    def clear_merge_files(self):
        self.merge_listbox.delete(0, tk.END)
        self.merge_files_data.clear()

    def move_merge_up(self):
        sel = self.merge_listbox.curselection()
        if sel and sel[0] > 0:
            idx = sel[0]
            val = self.merge_listbox.get(idx)
            data = self.merge_files_data.pop(idx)
            self.merge_listbox.delete(idx)
            self.merge_listbox.insert(idx - 1, val)
            self.merge_files_data.insert(idx - 1, data)
            self.merge_listbox.select_set(idx - 1)

    def move_merge_down(self):
        sel = self.merge_listbox.curselection()
        if sel and sel[0] < self.merge_listbox.size() - 1:
            idx = sel[0]
            val = self.merge_listbox.get(idx)
            data = self.merge_files_data.pop(idx)
            self.merge_listbox.delete(idx)
            self.merge_listbox.insert(idx + 1, val)
            self.merge_files_data.insert(idx + 1, data)
            self.merge_listbox.select_set(idx + 1)

    def run_merge_threaded(self):
        if len(self.merge_files_data) < 2:
            messagebox.showwarning("Insufficient Files", "Please add at least 2 PDF files to merge.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile="Merged_Document.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not save_path:
            return

        self.btn_run_merge.config(state="disabled")
        self.set_status(f"Merging {len(self.merge_files_data)} files...")

        def worker():
            try:
                core.merge_pdfs(self.merge_files_data, save_path, add_bookmarks=True)
                self.after(0, lambda: messagebox.showinfo("Success", f"Merged {len(self.merge_files_data)} files successfully!\nSaved to: {save_path}"))
                self.after(0, lambda: self.set_status("Merge complete."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Merge Error", str(e)))
                self.after(0, lambda: self.set_status(f"Error: {e}"))
            finally:
                self.after(0, lambda: self.btn_run_merge.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # TAB 3: 3-UP A4 CONVERTER
    # -------------------------------------------------------------------------
    def create_3up_tab(self):
        frame = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(frame, text="3-Up Print Prep")

        self.threeup_path_var = tk.StringVar()
        self.threeup_info_var = tk.StringVar(value="No file loaded")

        f_frame = ttk.LabelFrame(frame, text="Source PDF Book", padding=12)
        f_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Entry(f_frame, textvariable=self.threeup_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(f_frame, text="Browse...", command=self.browse_3up_file).pack(side=tk.RIGHT)
        ttk.Label(f_frame, textvariable=self.threeup_info_var, font=("Helvetica", 10, "italic")).pack(fill=tk.X, pady=(6, 0))

        opt_frame = ttk.LabelFrame(frame, text="Layout Options", padding=12)
        opt_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(opt_frame, text="Pages per Sheet:").grid(row=0, column=0, sticky="w", pady=4)
        self.threeup_cols_var = tk.IntVar(value=3)
        cols_combo = ttk.Combobox(opt_frame, textvariable=self.threeup_cols_var, values=[2, 3, 4], state="readonly", width=8)
        cols_combo.grid(row=0, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(opt_frame, text="Arrangement:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(opt_frame, text="A4 Landscape Horizontal (66.7% paper savings)", font=("Helvetica", 10, "bold")).grid(row=1, column=1, sticky="w", padx=8, pady=4)

        self.btn_run_3up = ttk.Button(frame, text="Generate 3-Up PDF", command=self.run_3up_threaded)
        self.btn_run_3up.pack(pady=10)

    def browse_3up_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                info = core.get_pdf_info(filename)
                self.threeup_path_var.set(filename)
                sheets = (info["total_pages"] + 2) // 3
                self.threeup_info_var.set(f"Loaded: {info['filename']} | {info['total_pages']} pages (-> ~{sheets} A4 sheets)")
                self.set_status(f"Loaded {info['filename']}")
            except Exception as e:
                messagebox.showerror("Error Loading PDF", str(e))

    def run_3up_threaded(self):
        src = self.threeup_path_var.get()
        if not src:
            messagebox.showwarning("Missing Input", "Please select a PDF file first.")
            return

        cols = self.threeup_cols_var.get()
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"{Path(src).stem}_{cols}up_a4.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not save_path:
            return

        self.btn_run_3up.config(state="disabled")
        self.set_status("Transforming into 3-Up landscape sheets...")

        def worker():
            try:
                res = core.create_nup_pdf(src, save_path, pages_per_sheet=cols)
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"3-Up imposition created!\nSource: {res['original_pages']} pages\nResult: {res['output_sheets']} sheets ({res['paper_savings_pct']}% paper saved)\nSaved to: {save_path}"
                ))
                self.after(0, lambda: self.set_status("3-Up generation complete."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Imposition Error", str(e)))
                self.after(0, lambda: self.set_status(f"Error: {e}"))
            finally:
                self.after(0, lambda: self.btn_run_3up.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # TAB 4: PDF TO DOCX
    # -------------------------------------------------------------------------
    def create_docx_tab(self):
        frame = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(frame, text="PDF to Word")

        self.docx_path_var = tk.StringVar()
        self.docx_info_var = tk.StringVar(value="No file loaded")

        f_frame = ttk.LabelFrame(frame, text="Source PDF Document", padding=12)
        f_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Entry(f_frame, textvariable=self.docx_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(f_frame, text="Browse...", command=self.browse_docx_file).pack(side=tk.RIGHT)
        ttk.Label(f_frame, textvariable=self.docx_info_var, font=("Helvetica", 10, "italic")).pack(fill=tk.X, pady=(6, 0))

        info_box = ttk.LabelFrame(frame, text="Conversion Notice", padding=12)
        info_box.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(info_box, text="Converts native layout, formatting, text, and tables into an editable Microsoft Word (.docx) document.", wraplength=480).pack()

        self.btn_run_docx = ttk.Button(frame, text="Convert to Word (.docx)", command=self.run_docx_threaded)
        self.btn_run_docx.pack(pady=10)

    def browse_docx_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                info = core.get_pdf_info(filename)
                self.docx_path_var.set(filename)
                self.docx_info_var.set(f"Loaded: {info['filename']} | {info['total_pages']} pages")
                self.set_status(f"Loaded {info['filename']}")
            except Exception as e:
                messagebox.showerror("Error Loading PDF", str(e))

    def run_docx_threaded(self):
        src = self.docx_path_var.get()
        if not src:
            messagebox.showwarning("Missing Input", "Please select a PDF file first.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"{Path(src).stem}.docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if not save_path:
            return

        self.btn_run_docx.config(state="disabled")
        self.set_status("Converting PDF to Word in background...")

        def worker():
            try:
                res = core.convert_pdf_to_docx(src, save_path)
                self.after(0, lambda: messagebox.showinfo("Success", f"Converted to Word document in {res['duration_seconds']}s!\nSaved to: {save_path}"))
                self.after(0, lambda: self.set_status("Word conversion complete."))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Conversion Error", str(e)))
                self.after(0, lambda: self.set_status(f"Error: {e}"))
            finally:
                self.after(0, lambda: self.btn_run_docx.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()


def run_app():
    app = PDFToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
