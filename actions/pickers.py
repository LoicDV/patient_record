from collections.abc import Sequence
from typing import Any

from console import ask_id, ask_text, print_table
from db import DbConnection
from models import Consultation, Doctor, Medication, Patient
from repositories import (
    consultations_repository,
    doctors_repository,
    medications_repository,
    patients_repository,
)

def pick(rows: Sequence[Any], columns: list[tuple[str, str]], label: str) -> Any:
    """Display records in a table and return the one whose ID the user chooses.

    Works with any model that has an 'id' attribute. It is typed with Any on
    purpose: the choose_* functions below declare the precise return type
    (Patient, Doctor...), so the code calling them is still fully checked.

    Args:
        rows (Sequence[Any]): Records to choose from
        columns (list[tuple[str, str]]): (attribute, header) pairs to display
        label (str): Name of the record, used in the question, e.g. 'Patient'

    Returns:
        Any: The chosen record, or None if the list is empty or the user
            typed 0 to cancel
    """
    if not rows:
        print("No results.")
        return None
    print_table(rows, columns)
    by_id = {row.id: row for row in rows if row.id is not None}
    chosen = ask_id(f"{label} ID", by_id.keys())
    return by_id[chosen] if chosen is not None else None

def choose_patient(conn: DbConnection) -> Patient | None:
    """Search patients by name (empty lists them all) and let the user pick one.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        Patient | None: The chosen patient, or None if cancelled
    """
    term = ask_text("Patient name (empty to list all)", required=False)
    rows = patients_repository.search(conn, term) if term else patients_repository.list_all(conn)
    columns = [("id", "ID"), ("last_name", "Last name"), ("first_name", "First name"),
               ("birth_date", "Birth date")]
    return pick(rows, columns, "Patient")

def choose_doctor(conn: DbConnection) -> Doctor | None:
    """List the doctors and let the user pick one.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        Doctor | None: The chosen doctor, or None if cancelled
    """
    columns = [("id", "ID"), ("last_name", "Last name"), ("first_name", "First name"),
               ("specialty", "Specialty")]
    return pick(doctors_repository.list_all(conn), columns, "Doctor")

def choose_medication(conn: DbConnection) -> Medication | None:
    """List the medications and let the user pick one.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        Medication | None: The chosen medication, or None if cancelled
    """
    columns = [("id", "ID"), ("name", "Name"), ("dosage", "Dosage")]
    return pick(medications_repository.list_all(conn), columns, "Medication")

def choose_consultation(conn: DbConnection, patient_id: int) -> Consultation | None:
    """List the consultations of a patient and let the user pick one.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        Consultation | None: The chosen consultation, or None if cancelled
    """
    columns = [("id", "ID"), ("consultation_date", "Date"), ("reason", "Reason"),
               ("doctor", "Doctor")]
    return pick(consultations_repository.list_for_patient(conn, patient_id), columns, "Consultation")
