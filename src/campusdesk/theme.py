"""Design tokens and colour helpers shared by the desktop, mobile and web interfaces.

Pure Python: no GUI toolkit is imported here, so it is easy to test.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass

Color = str  # "#rrggbb"


def hex_to_rgb(color: Color) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(r: float, g: float, b: float) -> Color:
    clamp = lambda v: max(0, min(255, round(v)))
    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"


def hex_to_rgba(color: Color, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """Kivy-style colour: four floats in 0..1."""
    r, g, b = hex_to_rgb(color)
    return r / 255, g / 255, b / 255, alpha


def lerp_color(a: Color, b: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    (r1, g1, b1), (r2, g2, b2) = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


def gradient_at(stops: tuple[Color, ...], t: float) -> Color:
    """Sample a multi-stop gradient at ``t`` in 0..1."""
    if len(stops) == 1:
        return stops[0]
    t = max(0.0, min(1.0, t)) * (len(stops) - 1)
    index = min(int(t), len(stops) - 2)
    return lerp_color(stops[index], stops[index + 1], t - index)


@dataclass(frozen=True)
class Theme:
    background: tuple[Color, ...] = ("#060b1d", "#0b1433", "#0f1a47", "#08293b")
    orbs: tuple[Color, ...] = ("#2563eb", "#10b981", "#8b5cf6")
    surface: Color = "#101936"
    surface_alt: Color = "#16204a"
    border: Color = "#26305f"
    field: Color = "#0a1128"
    text: Color = "#f1f5ff"
    muted: Color = "#8a95c9"
    primary: Color = "#3b82f6"
    primary_hover: Color = "#60a5fa"
    success: Color = "#10b981"
    warning: Color = "#f59e0b"
    danger: Color = "#ef4444"
    danger_hover: Color = "#f87171"
    chips: tuple[Color, ...] = (
        "#60a5fa", "#34d399", "#fbbf24", "#f472b6", "#a78bfa",
        "#22d3ee", "#fb923c", "#a3e635", "#e879f9", "#2dd4bf",
    )
    font_candidates: tuple[str, ...] = (
        "Inter", "SF Pro Display", "Segoe UI Variable", "Segoe UI",
        "Helvetica Neue", "Ubuntu", "Cantarell", "DejaVu Sans",
    )


THEME = Theme()


_SALT = 1  # chosen so the bundled demo data gets distinct colours


def _stable_index(text: str, modulo: int) -> int:
    """CRC32-based, so it is identical on every run, platform and interface."""
    return zlib.crc32(f"{_SALT}:{text.casefold()}".encode("utf-8")) % modulo


def course_color(course: str, theme: Theme = THEME) -> Color:
    """Each course always gets the same accent colour."""
    return theme.chips[_stable_index(course, len(theme.chips))]


def avatar_color(name: str, theme: Theme = THEME) -> Color:
    return theme.chips[_stable_index(name, len(theme.chips))]
