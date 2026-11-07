from psycopg import errors

from actions.pickers import choose_medication, choose_patient
from console import ask_choice, print_table, print_title
from db import DbConnection
from models import Severity
from repositories import allergic_to_repository

def add_allergy(conn: DbConnection) -> None:
    """Record that a patient is allergic to a medication.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Add an allergy")
    patient = choose_patient(conn)
    if patient is None or patient.id is None:
        return

    print("\nCurrent allergies")
    print_table(
        allergic_to_repository.list_for_patient(conn, patient.id),
        [("medication", "Medication"), ("dosage", "Dosage"), ("severity", "Severity")],
    )

    print()
    medication = choose_medication(conn)
    if medication is None:
        return
    severity = Severity(ask_choice("Severity", Severity.values()))

    try:
        allergic_to_repository.add(conn, patient.id, medication.id, severity)
    except errors.UniqueViolation:
        print("This allergy is already recorded.")
        return
    print(f"Allergy of {patient.full_name} to {medication.label} recorded.")
