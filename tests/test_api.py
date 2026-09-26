"""
REST API and Web route unit tests.
"""

import io
import shutil
import tempfile
import unittest
from pathlib import Path

from web.app import create_app
from tests.helpers import create_test_pdf


class TestWebApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_web_api_"))
        self.app = create_app(test_config={
            "TESTING": True,
            "UPLOAD_FOLDER": str(self.temp_dir)
        })
        self.client = self.app.test_client()

        self.doc1 = create_test_pdf(self.temp_dir / "sample1.pdf", num_pages=5, title="Sample 1")
        self.doc2 = create_test_pdf(self.temp_dir / "sample2.pdf", num_pages=3, title="Sample 2")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _upload(self, filepath: Path) -> str:
        """Helper to upload a file and return file_id."""
        with open(filepath, "rb") as f:
            data = {"file": (f, filepath.name)}
            res = self.client.post("/upload", data=data, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 200)
            return res.get_json()["id"]

    def test_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data["status"], "healthy")
        self.assertIn("version", json_data)

    def test_index_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"PDF Toolkit", res.data)

    def test_upload_invalid_extension(self):
        data = {"file": (io.BytesIO(b"dummy text"), "test.txt")}
        res = self.client.post("/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_upload_corrupt_pdf(self):
        data = {"file": (io.BytesIO(b"not a valid pdf header"), "test.pdf")}
        res = self.client.post("/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn("signature", res.get_json()["error"])

    def test_upload_and_info(self):
        fid = self._upload(self.doc1)
        res = self.client.post("/info", json={"file": fid})
        self.assertEqual(res.status_code, 200)
        info = res.get_json()
        self.assertEqual(info["total_pages"], 5)

    def test_extract_endpoint(self):
        fid = self._upload(self.doc1)
        res = self.client.post("/extract", json={"file": fid, "ranges": "1-2", "mode": "extract"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF-"))

    def test_split_endpoint(self):
        fid = self._upload(self.doc1)
        res = self.client.post("/extract", json={"file": fid, "ranges": "1-2, 3-5", "mode": "split"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/zip")

    def test_merge_endpoint(self):
        fid1 = self._upload(self.doc1)
        fid2 = self._upload(self.doc2)
        res = self.client.post("/merge", json={"files": [fid1, fid2]})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")

    def test_extract_merge_endpoint(self):
        fid1 = self._upload(self.doc1)
        fid2 = self._upload(self.doc2)
        payload = {
            "files": [
                {"id": fid1, "ranges": "1"},
                {"id": fid2, "ranges": "1-2"}
            ]
        }
        res = self.client.post("/extract_merge", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")

    def test_3up_endpoint(self):
        fid = self._upload(self.doc1)
        res = self.client.post("/api/3up", json={"file": fid, "cols": 3})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")

    def test_docx_endpoint(self):
        fid = self._upload(self.doc2)
        res = self.client.post("/api/to_docx", json={"file": fid, "start_page": 0, "end_page": 1})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def test_compress_endpoint(self):
        fid = self._upload(self.doc1)
        res = self.client.post("/compress", json={"file": fid, "level": "medium"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")
        self.assertIn("X-Reduction-Pct", res.headers)

    def test_clean_endpoint(self):
        res = self.client.post("/api/clean")
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.get_json())


if __name__ == "__main__":
    unittest.main()
