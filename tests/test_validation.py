import unittest

from campusdesk.core.errors import ValidationError
from campusdesk.core.validation import (
    validate_age, validate_course, validate_name, validate_student,
)


class ValidationTests(unittest.TestCase):
    def test_name_is_trimmed_and_collapsed(self):
        self.assertEqual(validate_name("  Ada    Lovelace "), "Ada Lovelace")

    def test_bad_names(self):
        for bad in ("", "   ", "R2D2", "x" * 61):
            with self.subTest(bad=bad), self.assertRaises(ValidationError) as ctx:
                validate_name(bad)
            self.assertEqual(ctx.exception.field, "name")

    def test_age_accepts_digits_only_within_range(self):
        self.assertEqual(validate_age(" 20 "), 20)
        self.assertEqual(validate_age(3), 3)
        for bad in ("", "abc", "2", "101", "-5", "20.5", "٢٠x"):
            with self.subTest(bad=bad), self.assertRaises(ValidationError) as ctx:
                validate_age(bad)
            self.assertEqual(ctx.exception.field, "age")

    def test_course(self):
        self.assertEqual(validate_course(" Computer   Science "), "Computer Science")
        with self.assertRaises(ValidationError):
            validate_course("  ")

    def test_validate_student_reports_first_problem(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_student("", "abc", "")
        self.assertEqual(ctx.exception.field, "name")
        self.assertEqual(validate_student("Sam", "21", "Law"), ("Sam", 21, "Law"))


if __name__ == "__main__":
    unittest.main()
