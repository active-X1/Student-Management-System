import json
import tempfile
import unittest
from pathlib import Path

from campusdesk.core import (
    MemoryRepository, SqliteRepository, StudentNotFoundError, StudentService,
    ValidationError, seed_demo,
)


class ServiceBehaviour:
    """Run against every repository implementation."""

    def make_repo(self):
        raise NotImplementedError

    def setUp(self):
        self.repo = self.make_repo()
        self.svc = StudentService(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_add_get_update_delete(self):
        s = self.svc.add_student(" Ada  Lovelace ", "21", "Mathematics")
        self.assertEqual((s.id, s.name, s.age), (1, "Ada Lovelace", 21))
        self.assertEqual(self.svc.get_student(1), s)
        u = self.svc.update_student(1, "Ada King", 22, "Computing")
        self.assertEqual((u.name, u.age, u.course), ("Ada King", 22, "Computing"))
        gone = self.svc.delete_student(1)
        self.assertEqual(gone.name, "Ada King")
        with self.assertRaises(StudentNotFoundError):
            self.svc.get_student(1)

    def test_ids_are_never_reused(self):
        a = self.svc.add_student("Ann", 20, "Law")
        self.svc.delete_student(a.id)
        b = self.svc.add_student("Ben", 20, "Law")
        self.assertGreater(b.id, a.id)

    def test_missing_ids_raise(self):
        for call in (lambda: self.svc.update_student(9, "A", 20, "B"), lambda: self.svc.delete_student(9)):
            with self.assertRaises(StudentNotFoundError):
                call()

    def test_invalid_input_is_not_stored(self):
        with self.assertRaises(ValidationError):
            self.svc.add_student("Ann", "x", "Law")
        self.assertEqual(self.svc.count(), 0)

    def test_search_matches_name_course_and_id(self):
        seed_demo(self.svc)
        self.assertEqual({s.name for s in self.svc.search("computer")}, {"Amara Okafor", "Chinedu Eze"})
        self.assertEqual([s.name for s in self.svc.search("fatima")], ["Fatima Bello"])
        self.assertEqual([s.id for s in self.svc.search("4")], [4])
        self.assertEqual(len(self.svc.search("")), 8)
        self.assertEqual(self.svc.search("zzz"), [])

    def test_sorting(self):
        seed_demo(self.svc)
        names = [s.name for s in self.svc.search(sort_by="name")]
        self.assertEqual(names, sorted(names, key=str.casefold))
        ages = [s.age for s in self.svc.search(sort_by="age", descending=True)]
        self.assertEqual(ages, sorted(ages, reverse=True))
        with self.assertRaises(ValueError):
            self.svc.search(sort_by="shoe_size")

    def test_stats(self):
        self.assertEqual(self.svc.stats().total, 0)
        self.assertEqual(self.svc.stats().average_age_text, "–")
        self.svc.add_student("A", 20, "Law")
        self.svc.add_student("B", 30, "law")      # same course, different case
        self.svc.add_student("C", 25, "Medicine")
        stats = self.svc.stats()
        self.assertEqual((stats.total, stats.course_count, stats.average_age), (3, 2, 25))
        self.assertEqual(stats.top_course, "Law")
        self.assertEqual(stats.by_course, {"Law": 2, "Medicine": 1})
        self.assertEqual(self.svc.courses(), ["Law", "Medicine"])

    def test_csv_export(self):
        self.svc.add_student("Ann, Jr.", 20, 'The "Arts"')
        text = self.svc.export_csv_text()
        self.assertEqual(text.splitlines()[0], "ID,Name,Age,Course")
        self.assertIn('"Ann, Jr."', text)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            self.assertEqual(self.svc.export_csv(path), 1)
            self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_import_original_json_format(self):
        data = {"2": {"Name": "Bola", "Age": "21", "Course": "Law"},
                "1": {"Name": "Ayo", "Age": 19, "Course": "Art"},
                "3": {"Name": "", "Age": "x", "Course": "Bad"},
                "4": "garbage"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "students.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(self.svc.import_json(path), 2)
        self.assertEqual([s.name for s in self.svc.search()], ["Ayo", "Bola"])

    def test_seed_demo_only_fills_an_empty_store(self):
        self.assertEqual(seed_demo(self.svc), 8)
        self.assertEqual(seed_demo(self.svc), 0)


class MemoryRepositoryTests(ServiceBehaviour, unittest.TestCase):
    def make_repo(self):
        return MemoryRepository()


class SqliteRepositoryTests(ServiceBehaviour, unittest.TestCase):
    def make_repo(self):
        return SqliteRepository(":memory:")

    def test_data_survives_reopening_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "students.db"
            first = SqliteRepository(path)
            StudentService(first).add_student("Ann", 20, "Law")
            first.close()
            second = SqliteRepository(path)
            self.assertEqual([s.name for s in StudentService(second).search()], ["Ann"])
            second.close()


if __name__ == "__main__":
    unittest.main()
