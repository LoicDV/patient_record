import io
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta
from unittest.mock import patch

import console
from models import Medication, Severity
from repositories.patients_repository import escape_like

def run_with_input(function, answers, *args, **kwargs):
    """Call function while input() returns answers in order. Returns (result, output)."""
    output = io.StringIO()
    with patch("builtins.input", side_effect=answers), redirect_stdout(output):
        result = function(*args, **kwargs)
    return result, output.getvalue()

class TestValidators(unittest.TestCase):
    def test_validate_email(self):
        self.assertIsNone(console.validate_email("jane.doe@example.com"))
        for invalid in ("jane", "jane@example", "jane doe@example.com", "@example.com"):
            with self.subTest(email=invalid):
                self.assertIsNotNone(console.validate_email(invalid))

    def test_validate_phone(self):
        self.assertIsNone(console.validate_phone("+32 470 12 34 56"))
        self.assertIsNotNone(console.validate_phone("call me"))

class TestAskText(unittest.TestCase):
    def test_required_field_asks_again_when_empty(self):
        result, output = run_with_input(console.ask_text, ["", "Alice"], "First name")
        self.assertEqual(result, "Alice")
        self.assertIn("required", output)

    def test_optional_field_returns_none(self):
        result, _ = run_with_input(console.ask_text, [""], "Phone", required=False)
        self.assertIsNone(result)

    def test_empty_answer_keeps_default(self):
        result, _ = run_with_input(console.ask_text, [""], "Name", default="Bob")
        self.assertEqual(result, "Bob")

    def test_max_length_and_validator(self):
        result, output = run_with_input(
            console.ask_text, ["x" * 10, "bad", "a@b.be"], "Email",
            max_length=8, validator=console.validate_email,
        )
        self.assertEqual(result, "a@b.be")
        self.assertIn("Maximum 8", output)
        self.assertIn("Invalid email", output)

class TestAskNumbersAndDates(unittest.TestCase):
    def test_ask_int_retries_until_in_bounds(self):
        result, _ = run_with_input(console.ask_int, ["abc", "0", "99", "5"], "Days",
                                   min_value=1, max_value=10)
        self.assertEqual(result, 5)

    def test_ask_id_accepts_only_listed_ids(self):
        result, output = run_with_input(console.ask_id, ["7", "3"], "Patient", {1, 3})
        self.assertEqual(result, 3)
        self.assertIn("not in the list", output)

    def test_ask_id_zero_cancels(self):
        result, _ = run_with_input(console.ask_id, ["0"], "Patient", {1, 3})
        self.assertIsNone(result)

    def test_ask_date_refuses_future_when_asked(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        result, output = run_with_input(console.ask_date, ["31/12/1990", tomorrow, "1990-12-31"],
                                        "Birth date", allow_future=False)
        self.assertEqual(result, date(1990, 12, 31))
        self.assertIn("format", output)
        self.assertIn("future", output)

    def test_ask_datetime_parses_value(self):
        result, _ = run_with_input(console.ask_datetime, ["2026-11-07 14:30"], "Date")
        self.assertEqual(result, datetime(2026, 11, 7, 14, 30))

class TestChoiceAndConfirmation(unittest.TestCase):
    def test_ask_choice_is_case_insensitive(self):
        result, _ = run_with_input(console.ask_choice, ["q", "f"], "Sex", ("M", "F", "X"))
        self.assertEqual(result, "F")

    def test_confirmation_defaults_to_no(self):
        cases = {"y": True, "YES": True, "": False, "n": False, "yes please": False}
        for answer, expected in cases.items():
            with self.subTest(answer=answer):
                result, _ = run_with_input(console.ask_confirmation, [answer], "Sure?")
                self.assertIs(result, expected)

class TestOutput(unittest.TestCase):
    def test_format_value(self):
        self.assertEqual(console.format_value(None), "-")
        self.assertEqual(console.format_value(date(2026, 1, 2)), "2026-01-02")
        self.assertEqual(console.format_value(datetime(2026, 1, 2, 9, 5)), "2026-01-02 09:05")
        self.assertEqual(console.format_value(42), "42")

    def test_truncate(self):
        self.assertEqual(console.truncate("short", 10), "short")
        self.assertEqual(console.truncate("a" * 20, 10), "aaaaaaa...")

    def test_print_table_aligns_columns(self):
        rows = [{"id": 1, "name": "Paracetamol"}, {"id": 12, "name": None}]
        output = io.StringIO()
        with redirect_stdout(output):
            console.print_table(rows, [("id", "ID"), ("name", "Name")])
        self.assertEqual(output.getvalue().splitlines(), [
            "ID  Name",
            "--  -----------",
            "1   Paracetamol",
            "12  -",
        ])

    def test_print_table_with_objects(self):
        rows = [Medication(1, "Ibuprofen", "400 mg")]
        output = io.StringIO()
        with redirect_stdout(output):
            console.print_table(rows, [("id", "ID"), ("label", "Medication")])
        self.assertEqual(output.getvalue().splitlines()[-1], "1   Ibuprofen 400 mg")

    def test_format_value_of_enum(self):
        self.assertEqual(console.format_value(Severity.SEVERE), "severe")

    def test_print_table_without_rows(self):
        output = io.StringIO()
        with redirect_stdout(output):
            console.print_table([], [("id", "ID")])
        self.assertEqual(output.getvalue().strip(), "No results.")

class TestEscapeLike(unittest.TestCase):
    def test_wildcards_are_escaped(self):
        self.assertEqual(escape_like("50%_off"), "50\\%\\_off")
        self.assertEqual(escape_like("Dupont"), "Dupont")

if __name__ == "__main__":
    unittest.main()
