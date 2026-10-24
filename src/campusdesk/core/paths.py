"""Where the database lives, per operating system."""

from __future__ import annotations

import os
import sys
from pathlib import Path

DB_ENV_VAR = "CAMPUSDESK_DB"
FOLDER = "CampusDesk"


def data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / FOLDER


def default_db_path() -> Path:
    override = os.environ.get(DB_ENV_VAR)
    return Path(override).expanduser() if override else data_dir() / "students.db"
