"""
Integration and functional tests for the core engine.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader

import core
from tests.helpers import create_test_pdf


class TestCoreEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_pdf_toolkit_"))
        self.doc1 = create_test_pdf(self.temp_dir / "doc1.pdf", num_pages=6, title="Doc 1")
        self.doc2 = create_test_pdf(self.temp_dir / "doc2.pdf", num_pages=4, title="Doc 2")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_pages(self):
        out = self.temp_dir / "extracted.pdf"
        res = core.extract_pages(self.doc1, out, "1-3, 5")
        self.assertTrue(out.exists())
        self.assertEqual(res["pages_extracted"], 4)

        reader = PdfReader(str(out))
        self.assertEqual(len(reader.pages), 4)

    def test_split_pages(self):
        out_zip = self.temp_dir / "split.zip"
        res = core.split_pages(self.doc1, out_zip, "1-2, 3-4, 5-6")
        self.assertTrue(out_zip.exists())
        self.assertEqual(res["parts_count"], 3)

    def test_merge_pdfs(self):
        out = self.temp_dir / "merged.pdf"
        res = core.merge_pdfs([self.doc1, self.doc2], out)
        self.assertTrue(out.exists())
        self.assertEqual(res["total_pages"], 10)

        reader = PdfReader(str(out))
        self.assertEqual(len(reader.pages), 10)

    def test_extract_and_merge(self):
        out = self.temp_dir / "em.pdf"
        items = [
            {"path": str(self.doc1), "ranges": "1-2"},
            {"path": str(self.doc2), "ranges": "3-4"}
        ]
        res = core.extract_and_merge(items, out)
        self.assertTrue(out.exists())
        self.assertEqual(res["total_pages"], 4)

    def test_imposition_3up(self):
        out = self.temp_dir / "3up.pdf"
        res = core.create_nup_pdf(self.doc1, out, pages_per_sheet=3)
        self.assertTrue(out.exists())
        self.assertEqual(res["original_pages"], 6)
        self.assertEqual(res["output_sheets"], 2)

        reader = PdfReader(str(out))
        self.assertEqual(len(reader.pages), 2)
        # Dimensions must be A4 landscape (842 x 595 points approximately)
        box = reader.pages[0].mediabox
        self.assertAlmostEqual(float(box.width), 841.89, delta=2.0)
        self.assertAlmostEqual(float(box.height), 595.28, delta=2.0)

    def test_pdf_info(self):
        info = core.get_pdf_info(self.doc1)
        self.assertEqual(info["total_pages"], 6)
        self.assertEqual(info["filename"], "doc1.pdf")
        self.assertFalse(info["is_encrypted"])
        self.assertIn("first_page", info)

    def test_compress_pdf(self):
        out = self.temp_dir / "compressed.pdf"
        res = core.compress_pdf(self.doc1, out, level="medium")
        self.assertTrue(out.exists())
        self.assertIn(res["method"], ["ghostscript", "pypdf_lossless"])
        self.assertGreater(res["compressed_size_bytes"], 0)

    def test_convert_docx(self):
        out = self.temp_dir / "converted.docx"
        res = core.convert_pdf_to_docx(self.doc2, out, start_page=0, end_page=2)
        self.assertTrue(out.exists())
        self.assertGreater(res["output_size_bytes"], 0)

    def test_cleanup_temp_files(self):
        dummy_file = self.temp_dir / "old_file.tmp"
        dummy_file.write_text("dummy")
        # cleanup with 0 hours should delete it
        deleted = core.cleanup_temp_files(directory=self.temp_dir, max_age_hours=0.0)
        self.assertGreaterEqual(deleted, 1)


if __name__ == "__main__":
    unittest.main()
