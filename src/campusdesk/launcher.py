"""Command-line launcher: picks an interface and opens the database."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from campusdesk import APP_NAME, __version__
from campusdesk.core import SqliteRepository, StudentService, default_db_path, seed_demo

INTERFACES = ("desktop", "mobile", "web", "terminal")
# Importing these names failing means the GUI toolkit isn't installed (not a bug in our code).
MISSING_TOOLKIT = {"tkinter", "_tkinter", "kivy", "nicegui"}
INSTALL_HINTS = {
    "desktop": "tkinter ships with Python. On Linux: sudo apt install python3-tk",
    "mobile": "pip install kivy",
    "web": "pip install nicegui",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="campus-desk",
        description=f"{APP_NAME}: student management for desktop, mobile preview, web and terminal.",
    )
    parser.add_argument("interface", nargs="?", choices=INTERFACES, default="desktop",
                        help="which interface to open (default: desktop)")
    parser.add_argument("--db", type=Path, help="database file (default: your user data folder)")
    parser.add_argument("--demo", action="store_true", help="add sample students if the database is empty")
    parser.add_argument("--import-json", type=Path, metavar="FILE",
                        help="import students from an old students.json, then continue")
    parser.add_argument("--port", type=int, default=8080, help="web port (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="web: don't open a browser tab")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def open_service(db: Path | None = None) -> StudentService:
    return StudentService(SqliteRepository(db or default_db_path()))


def _load_interface(name: str):
    if name == "desktop":
        from campusdesk.interfaces.desktop import run
    elif name == "mobile":
        from campusdesk.interfaces.mobile import run
    elif name == "web":
        from campusdesk.interfaces.web import run
    else:
        from campusdesk.interfaces.terminal import run
    return run


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = open_service(args.db)
    if args.import_json:
        try:
            print(f"Imported {service.import_json(args.import_json)} students from {args.import_json}.")
        except (OSError, ValueError) as err:
            print(f"Could not import {args.import_json}: {err}", file=sys.stderr)
            return 1
    if args.demo:
        seed_demo(service)

    name = args.interface
    try:
        run = _load_interface(name)
    except ImportError as err:
        if err.name not in MISSING_TOOLKIT:
            raise
        print(f"The {name} interface needs '{err.name}', which isn't installed.\n"
              f"  → {INSTALL_HINTS.get(name, '')}\nOpening the terminal interface instead.\n", file=sys.stderr)
        run = _load_interface("terminal")
    return run(service, port=args.port, open_browser=not args.no_browser) or 0
