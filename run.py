"""Convenience launcher that needs no installation:  python run.py [desktop|mobile|web|terminal]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from campusdesk.launcher import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
