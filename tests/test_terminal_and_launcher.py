import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from campusdesk.core import MemoryRepository, StudentService, seed_demo
from campusdesk.interfaces.terminal import TerminalApp, render_table
from campusdesk.launcher import build_parser, main


def drive(service, answers):
    """Run the terminal app with scripted answers; return everything it printed."""
    feed = iter(answers)
    out = []
    app = TerminalApp(service, input_fn=lambda _p: next(feed), print_fn=lambda *a: out.append(" ".join(map(str, a))), color=False)
    code = app.run()
    return code, "\n".join(out)


class TerminalTests(unittest.TestCase):
    def setUp(self):
        self.svc = StudentService(MemoryRepository())

    def test_add_with_retry_on_bad_input(self):
        code, out = drive(self.svc, ["1", "Ada Lovelace", "abc", "21", "Maths", "0"])
        self.assertEqual(code, 0)
        self.assertIn("Age must be a whole number", out)
        self.assertEqual([(s.name, s.age) for s in self.svc.search()], [("Ada Lovelace", 21)])

    def test_update_keeps_values_on_blank(self):
        self.svc.add_student("Ann", 20, "Law")
        drive(self.svc, ["4", "1", "", "25", "", "0"])
        s = self.svc.get_student(1)
        self.assertEqual((s.name, s.age, s.course), ("Ann", 25, "Law"))

    def test_delete_needs_confirmation(self):
        self.svc.add_student("Ann", 20, "Law")
        drive(self.svc, ["5", "1", "n", "0"])
        self.assertEqual(self.svc.count(), 1)
        drive(self.svc, ["5", "1", "y", "0"])
        self.assertEqual(self.svc.count(), 0)

    def test_unknown_id_and_menu_choice_are_reported(self):
        _, out = drive(self.svc, ["5", "99", "4", "x", "9", "0"])
        self.assertIn("No student with ID 99", out)
        self.assertIn("valid ID", out)
        self.assertIn("choose a number", out)

    def test_search_stats_export(self):
        seed_demo(self.svc)
        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "out.csv")
            _, out = drive(self.svc, ["3", "medicine", "6", "7", target, "0"])
            self.assertTrue(Path(target).read_text(encoding="utf-8").startswith("ID,Name,Age,Course"))
        self.assertIn("Fatima Bello", out)
        self.assertNotIn("Daniel Mensah", out.split("Statistics")[0])
        self.assertIn("Average age", out)

    def test_eof_exits_cleanly(self):
        def boom(_):
            raise EOFError
        app = TerminalApp(self.svc, input_fn=boom, print_fn=lambda *a: None, color=False)
        self.assertEqual(app.run(), 0)

    def test_render_table(self):
        self.assertIn("No students", render_table([]))
        seed_demo(self.svc)
        lines = render_table(self.svc.search()).splitlines()
        self.assertEqual(len(lines), 2 + 8)
        self.assertEqual(len({len(l.rstrip()) <= len(lines[1]) for l in lines}), 1)


class LauncherTests(unittest.TestCase):
    def test_parser_defaults(self):
        args = build_parser().parse_args([])
        self.assertEqual((args.interface, args.port, args.demo), ("desktop", 8080, False))

    def test_terminal_with_demo_and_temp_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "s.db"
            out = io.StringIO()
            with contextlib.redirect_stdout(out), unittest.mock.patch("builtins.input", side_effect=["2", "0"]):
                code = main(["terminal", "--db", str(db), "--demo"])
            self.assertEqual(code, 0)
            self.assertIn("Amara Okafor", out.getvalue())
            self.assertTrue(db.exists())

    def test_missing_toolkit_falls_back_to_terminal(self):
        # tkinter / kivy / nicegui are absent in CI-like environments; the launcher must not crash.
        import importlib.util
        if importlib.util.find_spec("tkinter") is not None:
            self.skipTest("tkinter is installed here")
        with tempfile.TemporaryDirectory() as tmp:
            err, out = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out), \
                    unittest.mock.patch("builtins.input", side_effect=["0"]):
                code = main(["desktop", "--db", str(Path(tmp) / "s.db")])
            self.assertEqual(code, 0)
            self.assertIn("tkinter", err.getvalue())


import unittest.mock  # noqa: E402  (kept at the bottom so the file reads top-down)

if __name__ == "__main__":
    unittest.main()
