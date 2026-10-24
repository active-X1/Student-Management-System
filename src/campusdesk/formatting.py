"""Small text helpers shared by the interfaces."""

from __future__ import annotations


def truncate(text: str, limit: int) -> str:
    """Shorten with an ellipsis so long names never overflow a card."""
    return text if len(text) <= limit else text[: max(0, limit - 1)].rstrip() + "…"
