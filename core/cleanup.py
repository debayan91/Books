"""
Temporary File Cleanup Management.
"""

import os
import time
import shutil
import logging
from pathlib import Path
from typing import Optional
from core.config import TEMP_DIR, TEMP_FILE_TTL_HOURS

logger = logging.getLogger("pdf_toolkit.cleanup")


def cleanup_temp_files(
    directory: Optional[Path] = None,
    max_age_hours: float = TEMP_FILE_TTL_HOURS,
    force_all: bool = False
) -> int:
    """
    Scans the temporary directory and removes files older than max_age_hours.
    If force_all is True, removes all files regardless of age.
    Returns the count of removed files/directories.
    """
    target_dir = directory or TEMP_DIR
    if not target_dir.exists():
        return 0

    now = time.time()
    cutoff_time = now - (max_age_hours * 3600)
    removed_count = 0

    for item in target_dir.iterdir():
        if item.name.startswith("."):
            continue
        try:
            stat = item.stat()
            file_mtime = stat.st_mtime
            if force_all or (file_mtime < cutoff_time):
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
                removed_count += 1
                logger.debug(f"Removed temporary item: {item.name}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary item {item}: {e}")

    logger.info(f"Cleaned up {removed_count} temporary items from {target_dir}")
    return removed_count
