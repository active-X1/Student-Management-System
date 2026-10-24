import os
import unittest
from pathlib import Path
from unittest import mock

from campusdesk.core import Student, default_db_path
from campusdesk.core.paths import DB_ENV_VAR
from campusdesk.theme import (
    THEME, avatar_color, course_color, gradient_at, hex_to_rgb, hex_to_rgba, lerp_color, rgb_to_hex,
)


class ModelTests(unittest.TestCase):
    def test_initials(self):
        self.assertEqual(Student(1, "Ada Lovelace", 20, "x").initials, "AL")
        self.assertEqual(Student(1, "madonna", 20, "x").initials, "MA")
        self.assertEqual(Student(1, "Mary Ann Smith", 20, "x").initials, "MS")
        self.assertEqual(Student(1, "  ", 20, "x").initials, "?")

    def test_matches(self):
        s = Student(7, "Ada Lovelace", 20, "Mathematics")
        for q in ("", "ada", "LOVE", "math", "7"):
            self.assertTrue(s.matches(q), q)
        for q in ("8", "bob"):
            self.assertFalse(s.matches(q), q)


class PathTests(unittest.TestCase):
    def test_env_override(self):
        with mock.patch.dict(os.environ, {DB_ENV_VAR: "/tmp/x/students.db"}):
            self.assertEqual(default_db_path(), Path("/tmp/x/students.db"))

    def test_default_location_ends_with_app_folder(self):
        env = {k: v for k, v in os.environ.items() if k != DB_ENV_VAR}
        with mock.patch.dict(os.environ, env, clear=True):
            path = default_db_path()
        self.assertEqual(path.name, "students.db")
        self.assertEqual(path.parent.name, "CampusDesk")


class ThemeTests(unittest.TestCase):
    def test_colour_helpers(self):
        self.assertEqual(rgb_to_hex(*hex_to_rgb("#3b82f6")), "#3b82f6")
        self.assertEqual(lerp_color("#000000", "#ffffff", 0.5), "#808080")
        self.assertEqual(lerp_color("#000000", "#ffffff", 9), "#ffffff")
        self.assertEqual(gradient_at(("#000000", "#ffffff", "#000000"), 0.5), "#ffffff")
        self.assertEqual(hex_to_rgba("#ff0000", 0.5), (1.0, 0.0, 0.0, 0.5))

    def test_accent_colours_are_stable_and_case_insensitive(self):
        self.assertEqual(course_color("Law"), course_color("law"))
        self.assertIn(avatar_color("Ada"), THEME.chips)
        self.assertEqual(avatar_color("Ada"), avatar_color("Ada"))


if __name__ == "__main__":
    unittest.main()


class SharedHelperTests(unittest.TestCase):
    def test_truncate(self):
        from campusdesk.formatting import truncate
        self.assertEqual(truncate("short", 10), "short")
        self.assertEqual(truncate("a very long course name", 10), "a very lo…")
        self.assertLessEqual(len(truncate("x" * 100, 12)), 12)

    def test_bundled_assets_exist(self):
        from campusdesk.resources import ASSETS, asset_path
        for name in ("logo.svg", "icon-64.png", "icon-256.png", "icon-512.png"):
            self.assertTrue((ASSETS / name).is_file(), name)
        self.assertTrue(asset_path("logo.svg").endswith("logo.svg"))

    def test_svg_is_well_formed(self):
        import xml.etree.ElementTree as ET
        from campusdesk.resources import ASSETS
        ET.parse(ASSETS / "logo.svg")

    def test_rounded_rect_geometry_is_pure_python(self):
        import importlib.util
        from campusdesk.resources import ASSETS
        spec = importlib.util.spec_from_file_location("geometry", ASSETS.parent / "interfaces" / "desktop" / "geometry.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rounded_rect_points = module.rounded_rect_points
        pts = rounded_rect_points(10, 20, 110, 70, 999)   # an oversized radius is clamped
        self.assertEqual(len(pts) % 2, 0)
        xs, ys = pts[0::2], pts[1::2]
        self.assertTrue(10 <= min(xs) and max(xs) <= 110 and 20 <= min(ys) and max(ys) <= 70)
