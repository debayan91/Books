"""
Legacy server compatibility module.
Delegates to web.app.create_app().
"""

import sys
from pathlib import Path

# Add project root to sys.path so imports work seamlessly if executed from inside pdf_extractor
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from web.app import create_app

app = create_app()

if __name__ == "__main__":
    from start import run_web
    run_web(port=5050)
