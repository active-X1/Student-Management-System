"""Entry point for the mobile build (Buildozer / python-for-android looks for ``main.py``).

It is also a handy way to preview the phone interface on a computer:  python main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from campusdesk.interfaces.mobile import run  # noqa: E402

if __name__ == "__main__":
    run()
