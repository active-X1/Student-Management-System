"""Locations of bundled files. No GUI imports, so every interface can use it."""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"


def asset_path(name: str) -> str:
    """Absolute path of a bundled asset, as a string (what GUI toolkits expect)."""
    return str(ASSETS / name)
