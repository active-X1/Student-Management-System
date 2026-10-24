"""Mobile interface (Kivy). Phone-first, and also runs on the desktop as a preview."""

import kivy  # noqa: F401  (raises ImportError early if Kivy is missing, so the launcher can fall back)
from kivy.utils import platform


def run(service=None, **options):
    """Open the app. On a desktop this uses a phone-shaped window; on a phone it is full screen."""
    if platform not in {"android", "ios"}:
        from kivy.config import Config

        Config.set("graphics", "width", "400")
        Config.set("graphics", "height", "820")
        Config.set("graphics", "resizable", "1")
        Config.set("input", "mouse", "mouse,disable_multitouch")  # no red dots on right-click
    from campusdesk.interfaces.mobile.app import run as _run

    return _run(service, **options)


__all__ = ["run"]
