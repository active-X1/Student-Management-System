"""Reusable Kivy widgets: aurora background, cards, pill buttons, inputs, toast."""

from __future__ import annotations

import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from campusdesk.theme import THEME, gradient_at, hex_to_rgb, hex_to_rgba

TEXT = hex_to_rgba(THEME.text)
MUTED = hex_to_rgba(THEME.muted)


def gradient_texture(stops: tuple[str, ...], steps: int = 96) -> Texture:
    """A 1×N vertical gradient texture, stretched to fill any size.

    Kivy textures start at the bottom row, so the buffer runs bottom → top.
    """
    texture = Texture.create(size=(1, steps), colorfmt="rgb")
    data = bytearray()
    for row in range(steps):
        data += bytes(hex_to_rgb(gradient_at(stops, 1 - row / (steps - 1))))
    texture.blit_buffer(bytes(data), colorfmt="rgb", bufferfmt="ubyte")
    texture.mag_filter = texture.min_filter = "linear"
    return texture


class AuroraBackground(Widget):
    """Full-screen gradient with softly drifting glow orbs."""

    RINGS = 10
    # centre x, centre y (fractions), radius (fraction of the long edge), drift dp x/y, speed, phase
    ORBS = ((0.10, 0.90, 0.55, 40, 28, 0.9, 0.0), (0.98, 0.52, 0.48, 34, 44, 0.7, 2.1), (0.18, 0.06, 0.58, 44, 30, 0.8, 4.2))

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._t = 0.0
        self._orbs: list[tuple[tuple, list[Ellipse]]] = []
        with self.canvas:
            Color(1, 1, 1, 1)
            self._rect = Rectangle(texture=gradient_texture(THEME.background), pos=self.pos, size=self.size)
            for index, spec in enumerate(self.ORBS):
                rings = []
                for _ in range(self.RINGS):
                    Color(*hex_to_rgba(THEME.orbs[index % len(THEME.orbs)], 0.045))
                    rings.append(Ellipse(pos=(0, 0), size=(0, 0)))
                self._orbs.append((spec, rings))
        self.bind(pos=self._layout, size=self._layout)
        self._event = Clock.schedule_interval(self._tick, 1 / 20)

    def _layout(self, *_args) -> None:
        self._rect.pos, self._rect.size = self.pos, self.size
        self._place()

    def _place(self) -> None:
        longest = max(self.width, self.height)
        for (fx, fy, radius, dx, dy, speed, phase), rings in self._orbs:
            cx = self.x + fx * self.width + math.sin(self._t * 0.35 * speed + phase) * dp(dx)
            cy = self.y + fy * self.height + math.cos(self._t * 0.28 * speed + phase) * dp(dy)
            for k, ellipse in enumerate(rings):
                r = radius * longest * (1 - k / self.RINGS * 0.92)
                ellipse.pos, ellipse.size = (cx - r, cy - r), (2 * r, 2 * r)

    def _tick(self, dt: float) -> None:
        self._t += dt
        self._place()

    def stop(self) -> None:
        self._event.cancel()


class Card(BoxLayout):
    """A rounded translucent panel with a hairline border."""

    fill = ListProperty(hex_to_rgba(THEME.surface, 0.82))
    stroke = ListProperty(hex_to_rgba("#ffffff", 0.10))
    radius = NumericProperty(dp(20))

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        with self.canvas.before:
            self._fill_color = Color(*self.fill)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._stroke_color = Color(*self.stroke)
            self._line = Line(rounded_rectangle=(self.x, self.y, 2, 2, 1), width=1)
        self.bind(pos=self._sync, size=self._sync, radius=self._sync, fill=self._recolor, stroke=self._recolor)
        self._sync()

    def _sync(self, *_args) -> None:
        w, h = max(self.width, 2), max(self.height, 2)
        r = max(1, min(self.radius, w / 2, h / 2))
        self._bg.pos, self._bg.size, self._bg.radius = self.pos, self.size, [r]
        self._line.rounded_rectangle = (self.x, self.y, w, h, r)

    def _recolor(self, *_args) -> None:
        self._fill_color.rgba, self._stroke_color.rgba = self.fill, self.stroke


class TappableCard(ButtonBehavior, Card):
    """A card that reacts to touch (used for list rows)."""

    _base_fill = hex_to_rgba(THEME.surface, 0.82)
    _down_fill = hex_to_rgba(THEME.surface_alt, 0.95)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bind(state=self._on_state)

    def _on_state(self, _instance, value: str) -> None:
        self.fill = self._down_fill if value == "down" else self._base_fill


class TextLabel(Label):
    """A single-line, left-aligned label that tracks its own size."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("max_lines", 1)
        kwargs.setdefault("color", TEXT)
        super().__init__(**kwargs)
        self.bind(size=self._fit_text)
        self._fit_text()

    def _fit_text(self, *_args) -> None:
        self.text_size = self.size


class PillButton(ButtonBehavior, Label):
    """A rounded button with a pressed state. Minimum touch height is 48dp."""

    fill = ListProperty(hex_to_rgba(THEME.primary))
    fill_down = ListProperty(hex_to_rgba(THEME.primary_hover))
    radius = NumericProperty(dp(16))

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", sp(16))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        kwargs.setdefault("color", (1, 1, 1, 1))
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*self.fill)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._sync, size=self._sync, radius=self._sync, fill=self._recolor,
                  fill_down=self._recolor, state=self._recolor)

    def _sync(self, *_args) -> None:
        self._bg.pos, self._bg.size = self.pos, self.size
        self._bg.radius = [max(1, min(self.radius, self.width / 2, self.height / 2))]

    def _recolor(self, *_args) -> None:
        self._color.rgba = self.fill_down if self.state == "down" else self.fill


class Fab(ButtonBehavior, Widget):
    """Circular floating action button with a drawn "+" (no icon font needed)."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(62), dp(62)))
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 0.35)
            self._shadow = Ellipse()
            self._color = Color(*hex_to_rgba(THEME.primary))
            self._disc = Ellipse()
            Color(1, 1, 1, 1)
            self._h = Line(width=dp(2.4), cap="round")
            self._v = Line(width=dp(2.4), cap="round")
        self.bind(pos=self._sync, size=self._sync, state=self._on_state)

    def _sync(self, *_args) -> None:
        self._shadow.pos, self._shadow.size = (self.x - dp(1), self.y - dp(4)), (self.width + dp(2), self.height + dp(2))
        self._disc.pos, self._disc.size = self.pos, self.size
        cx, cy, arm = self.center_x, self.center_y, self.width * 0.21
        self._h.points = [cx - arm, cy, cx + arm, cy]
        self._v.points = [cx, cy - arm, cx, cy + arm]

    def _on_state(self, _instance, value: str) -> None:
        self._color.rgba = hex_to_rgba(THEME.primary_hover if value == "down" else THEME.primary)


class Avatar(Label):
    """A coloured circle holding the student's initials."""

    def __init__(self, tint: str, **kwargs) -> None:
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(48), dp(48)))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", sp(16))
        kwargs.setdefault("color", hex_to_rgba("#0b1020"))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*hex_to_rgba(tint))
            self._disc = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_args) -> None:
        self._disc.pos, self._disc.size = self.pos, self.size


class RoundedInput(BoxLayout):
    """A single-line text field inside a rounded box with a focus ring."""

    def __init__(self, hint_text: str = "", input_filter=None, input_type: str = "text", **kwargs) -> None:
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(54))
        kwargs.setdefault("padding", [dp(16), 0])
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*hex_to_rgba(THEME.field, 0.95))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            self._ring_color = Color(*hex_to_rgba(THEME.border))
            self._ring = Line(rounded_rectangle=(self.x, self.y, 2, 2, 1), width=1.2)
        self.input = TextInput(
            hint_text=hint_text, multiline=False, write_tab=False, input_filter=input_filter,
            input_type=input_type, font_size=sp(16), background_normal="", background_active="",
            background_color=(0, 0, 0, 0), foreground_color=TEXT, cursor_color=hex_to_rgba(THEME.primary),
            hint_text_color=hex_to_rgba(THEME.muted, 0.8), selection_color=hex_to_rgba(THEME.primary, 0.4),
        )
        self.add_widget(self.input)
        self.bind(pos=self._sync, size=self._sync)
        self.input.bind(focus=self._on_focus, size=self._center_text)
        Clock.schedule_once(self._center_text, 0)
        self._sync()

    @property
    def text(self) -> str:
        return self.input.text

    @text.setter
    def text(self, value: str) -> None:
        self.input.text = value

    def _sync(self, *_args) -> None:
        w, h = max(self.width, 2), max(self.height, 2)
        self._bg.pos, self._bg.size = self.pos, self.size
        self._ring.rounded_rectangle = (self.x, self.y, w, h, min(dp(14), w / 2, h / 2))

    def _on_focus(self, _instance, focused: bool) -> None:
        self._ring_color.rgba = hex_to_rgba(THEME.primary if focused else THEME.border)

    def _center_text(self, *_args) -> None:
        pad = max(0, (self.input.height - self.input.line_height) / 2)
        self.input.padding = [0, pad, 0, pad]


class Toast(Card):
    """A short message pill that fades in and out."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dp(48))
        kwargs.setdefault("padding", [dp(18), 0])
        kwargs.setdefault("fill", hex_to_rgba(THEME.surface_alt, 0.98))
        kwargs.setdefault("radius", dp(24))
        super().__init__(**kwargs)
        self.opacity = 0
        self.label = Label(font_size=sp(14), color=TEXT, bold=True)
        self.add_widget(self.label)

    def show(self, text: str, ok: bool = True, duration: float = 2.2) -> None:
        self.label.text = text
        self.label.color = hex_to_rgba(THEME.success if ok else THEME.danger_hover)
        self.label.texture_update()
        self.width = min(self.label.texture_size[0] + dp(44), dp(340))
        Animation.cancel_all(self)
        (Animation(opacity=1, d=0.15) + Animation(opacity=1, d=duration) + Animation(opacity=0, d=0.3)).start(self)
