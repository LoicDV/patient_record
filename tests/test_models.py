import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from models import Allergy, Medication, Patient, PrescriptionDraft, Severity

def make_patient(**changes) -> Patient:
    """Build a valid patient, with some fields replaced."""
    fields = {
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_date": date(1990, 6, 15),
        "sex": "F",
        "email": "jane.doe@example.com",
    }
    fields.update(changes)
    return Patient(**fields)

class TestPatient(unittest.TestCase):
    def test_full_name(self):
        self.assertEqual(make_patient().full_name, "Jane Doe")

    def test_age_before_and_after_birthday(self):
        patient = make_patient()
        self.assertEqual(patient.age_on(date(2026, 6, 14)), 35)
        self.assertEqual(patient.age_on(date(2026, 6, 15)), 36)

    def test_invalid_sex_is_refused(self):
        with self.assertRaises(ValueError):
            make_patient(sex="Z")

    def test_future_birth_date_is_refused(self):
        with self.assertRaises(ValueError):
            make_patient(birth_date=date(date.today().year + 1, 1, 1))

    def test_new_patient_has_no_id(self):
        self.assertIsNone(make_patient().id)

class TestAllergy(unittest.TestCase):
    def test_severity_from_database_text(self):
        allergy = Allergy(medication_id=1, medication="Ibuprofen", dosage="400 mg",
                          severity="severe")  # type: ignore[arg-type]  # as read from the database
        self.assertIs(allergy.severity, Severity.SEVERE)

    def test_unknown_severity_is_refused(self):
        with self.assertRaises(ValueError):
            Allergy(1, "Ibuprofen", "400 mg", "extreme")  # type: ignore[arg-type]

    def test_severity_values(self):
        self.assertEqual(Severity.values(), ["mild", "moderate", "severe"])

class TestMedication(unittest.TestCase):
    def test_label(self):
        self.assertEqual(Medication(1, "Paracetamol", "1 g").label, "Paracetamol 1 g")

    def test_is_immutable(self):
        medication = Medication(1, "Paracetamol", "1 g")
        with self.assertRaises(FrozenInstanceError):
            medication.name = "Aspirin"  # type: ignore[misc]

class TestPrescriptionDraft(unittest.TestCase):
    def test_valid_duration(self):
        self.assertEqual(PrescriptionDraft(1, "1 tablet", 7).duration_days, 7)

    def test_invalid_duration_is_refused(self):
        for duration in (0, -3, 40000):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                PrescriptionDraft(1, "1 tablet", duration)

if __name__ == "__main__":
    unittest.main()
