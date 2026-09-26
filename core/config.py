"""
Central Configuration for PDF Toolkit.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / ".temp_storage"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Server Defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5050  # Avoid macOS AirPlay Receiver on port 5000
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB maximum upload size

# File Lifetimes
TEMP_FILE_TTL_HOURS = 2.0  # Files older than 2 hours in .temp_storage will be cleaned

# Supported Formats
ALLOWED_EXTENSIONS = {".pdf"}
