"""Custom canvas-drawn widgets: header, stat cards, rounded buttons, search box."""

from __future__ import annotations

import datetime
import math
import tkinter as tk
from typing import Callable

from campusdesk import APP_NAME, __version__
from campusdesk.formatting import truncate
from campusdesk.interfaces.desktop.geometry import rounded_rect_points
from campusdesk.resources import ASSETS
from campusdesk.theme import Theme, gradient_at, lerp_color


class RoundedButton(tk.Canvas):
    """A pill-shaped button with a smooth hover fade and an enabled/disabled state."""

    def __init__(self, master, text: str, command: Callable[[], None], *, fill: str, hover: str,
                 bg: str, font: tuple, fg: str = "#ffffff", width: int = 130, height: int = 40,
                 radius: int = 14) -> None:
        super().__init__(master, width=width, height=height, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self._command, self._fill, self._hover, self._bg = command, fill, hover, bg
        self._w, self._h = width, height
        self._current, self._job, self._enabled = fill, None, True
        self._shape = self.create_polygon(
            rounded_rect_points(1, 1, width - 1, height - 1, radius), smooth=True, fill=fill, outline="")
        self._label = self.create_text(width / 2, height / 2, text=text, fill=fg, font=font)
        self.bind("<Enter>", lambda _e: self._fade(self._hover))
        self.bind("<Leave>", lambda _e: self._fade(self._fill))
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_release(self, event: tk.Event) -> None:
        if self._enabled and 0 <= event.x <= self._w and 0 <= event.y <= self._h:
            self._command()

    def _fade(self, target: str, steps: int = 6) -> None:
        if not self._enabled:
            return
        if self._job:
            self.after_cancel(self._job)
        start = self._current

        def step(i: int = 1) -> None:
            self._current = lerp_color(start, target, i / steps)
            self.itemconfigure(self._shape, fill=self._current)
            self._job = self.after(16, step, i + 1) if i < steps else None

        step()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self._current = self._fill if enabled else lerp_color(self._fill, self._bg, 0.7)
        self.itemconfigure(self._shape, fill=self._current)
        self.itemconfigure(self._label, fill="#ffffff" if enabled else lerp_color("#ffffff", self._bg, 0.6))
        self.configure(cursor="hand2" if enabled else "arrow")


class StatCard(tk.Canvas):
    """A rounded dashboard tile: big value, small caption, coloured accent bar."""

    def __init__(self, master, caption: str, accent: str, theme: Theme, family: str, *, bg: str, height: int = 92) -> None:
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0)
        self._caption, self._accent, self._theme, self._family = caption, accent, theme, family
        self._value, self._small = "–", False
        self.bind("<Configure>", lambda _e: self._redraw())

    def set_value(self, value: str, small: bool = False) -> None:
        self._value, self._small = value, small
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 40:  # not laid out yet
            return
        t = self._theme
        self.create_polygon(rounded_rect_points(1, 1, w - 1, h - 1, 18), smooth=True, fill=t.surface, outline=t.border)
        self.create_polygon(rounded_rect_points(14, 20, 18, h - 20, 2), smooth=True, fill=self._accent, outline="")
        size = 14 if self._small else 26
        self.create_text(32, h * 0.42, anchor="w", text=truncate(self._value, 22 if self._small else 10),
                         fill=t.text, font=(self._family, size, "bold"))
        self.create_text(32, h - 22, anchor="w", text=self._caption.upper(), fill=t.muted,
                         font=(self._family, 9, "bold"))


class GradientHeader(tk.Canvas):
    """Deep gradient with slowly drifting glow orbs, the logo and the app title."""

    HEIGHT, STRIP, RINGS, FRAME_MS = 120, 3, 16, 50

    def __init__(self, master, theme: Theme, family: str) -> None:
        super().__init__(master, height=self.HEIGHT, bg=theme.background[0], highlightthickness=0, bd=0)
        self.theme, self.family = theme, family
        self._t, self._job = 0.0, None
        self._orbs: list[dict] = []
        try:
            self._logo = tk.PhotoImage(file=str(ASSETS / "icon-64.png"))
        except tk.TclError:
            self._logo = None
        self.bind("<Configure>", lambda _e: self._redraw())

    def _redraw(self) -> None:
        self.delete("all")
        w, h, t = self.winfo_width(), self.HEIGHT, self.theme
        if w < 50:
            return
        for y in range(0, h, self.STRIP):
            base = gradient_at(t.background, 0.25 + 0.5 * y / h)
            self.create_rectangle(0, y, w, y + self.STRIP + 1, fill=lerp_color(base, t.background[0], (y / h) ** 1.6), outline="")
        self._orbs = []
        specs = [(0.12, 0.2, 150, 30, 14, 0.9, 0.0), (0.58, 0.9, 130, 40, 10, 0.7, 2.1), (0.94, 0.15, 140, 26, 16, 0.8, 4.2)]
        for i, (fx, fy, radius, dx, dy, speed, phase) in enumerate(specs):
            colour, cx, cy, tag = t.orbs[i % len(t.orbs)], fx * w, fy * h, f"orb{i}"
            for ring in range(self.RINGS):
                k = ring / (self.RINGS - 1)
                r = radius * (1 - k * 0.95)
                glow = lerp_color(gradient_at(t.background, 0.4), colour, (k ** 2.2) * 0.45)
                self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=glow, outline="", tags=(tag,))
            self._orbs.append({"tag": tag, "dx": dx, "dy": dy, "speed": speed, "phase": phase, "ox": 0.0, "oy": 0.0})
        if self._logo is not None:
            self.create_image(30, h / 2, image=self._logo, anchor="w")
        self.create_text(112, h / 2 - 14, anchor="w", text=APP_NAME, fill=t.text, font=(self.family, 24, "bold"))
        self.create_text(114, h / 2 + 18, anchor="w", text="Manage students, courses and records", fill=t.muted, font=(self.family, 11))
        today = datetime.date.today().strftime("%A, %d %B %Y")
        self.create_text(w - 28, h / 2 - 10, anchor="e", text=today, fill=t.text, font=(self.family, 11))
        self.create_text(w - 28, h / 2 + 14, anchor="e", text=f"v{__version__}", fill=t.muted, font=(self.family, 9))

    def start(self) -> None:
        if self._job is None:
            self._tick()

    def stop(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def _tick(self) -> None:
        self._t += self.FRAME_MS / 1000
        for orb in self._orbs:
            nx = math.sin(self._t * 0.35 * orb["speed"] + orb["phase"]) * orb["dx"]
            ny = math.cos(self._t * 0.28 * orb["speed"] + orb["phase"]) * orb["dy"]
            self.move(orb["tag"], nx - orb["ox"], ny - orb["oy"])
            orb["ox"], orb["oy"] = nx, ny
        self._job = self.after(self.FRAME_MS, self._tick)


class SearchEntry(tk.Frame):
    """A single-line search box with placeholder text and a change callback."""

    PLACEHOLDER = "Search by name, course or ID…"

    def __init__(self, master, theme: Theme, family: str, on_change: Callable[[str], None], *, bg: str) -> None:
        super().__init__(master, bg=bg)
        self._theme, self._on_change, self._placeholder_on = theme, on_change, False
        self._var = tk.StringVar()
        self.entry = tk.Entry(
            self, textvariable=self._var, font=(family, 12), bg=theme.field, fg=theme.text,
            insertbackground=theme.primary, relief="flat", bd=0, highlightthickness=1,
            highlightbackground=theme.border, highlightcolor=theme.primary)
        self.entry.pack(fill="x", ipady=9)
        self.entry.bind("<FocusIn>", lambda _e: self._hide_placeholder())
        self.entry.bind("<FocusOut>", lambda _e: self._show_placeholder())
        self._var.trace_add("write", lambda *_: self._changed())
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        if not self._var.get():
            self._placeholder_on = True
            self._var.set(self.PLACEHOLDER)
            self.entry.configure(fg=self._theme.muted)

    def _hide_placeholder(self) -> None:
        if self._placeholder_on:
            self._placeholder_on = False
            self._var.set("")
            self.entry.configure(fg=self._theme.text)

    def _changed(self) -> None:
        if not self._placeholder_on:
            self._on_change(self._var.get())

    def query(self) -> str:
        return "" if self._placeholder_on else self._var.get().strip()

    def clear(self) -> None:
        self._hide_placeholder()
        self._var.set("")
        if self.focus_get() is not self.entry:
            self._show_placeholder()

    def focus(self) -> None:
        self.entry.focus_set()
