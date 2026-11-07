from collections import defaultdict

from psycopg import errors

from actions.pickers import choose_patient
from console import (
    ask_choice,
    ask_confirmation,
    ask_date,
    ask_text,
    format_value,
    print_table,
    print_title,
    validate_email,
    validate_phone,
)
from db import DbConnection
from models import SEXES, Patient, Prescription
from repositories import (
    allergic_to_repository,
    consultations_repository,
    patients_repository,
    prescriptions_repository,
)

PATIENT_COLUMNS = [
    ("id", "ID"),
    ("last_name", "Last name"),
    ("first_name", "First name"),
    ("birth_date", "Birth date"),
    ("age", "Age"),
    ("sex", "Sex"),
    ("phone", "Phone"),
    ("email", "Email"),
]

def ask_patient(current: Patient | None = None) -> Patient:
    """Ask for every field of a patient.

    Args:
        current (Patient | None, optional): Patient being updated; an empty
            answer then keeps its current value. Defaults to None.

    Returns:
        Patient: A new Patient object, with the id of current if given
    """
    return Patient(
        first_name=ask_text("First name", max_length=100,
                            default=current.first_name if current else None),
        last_name=ask_text("Last name", max_length=100,
                           default=current.last_name if current else None),
        birth_date=ask_date("Birth date", allow_future=False,
                            default=current.birth_date if current else None),
        sex=ask_choice("Sex", SEXES, default=current.sex if current else None),
        phone=ask_text("Phone (optional)", required=False, max_length=20,
                       validator=validate_phone, default=current.phone if current else None),
        email=ask_text("Email", max_length=320, validator=validate_email,
                       default=current.email if current else None),
        id=current.id if current else None,
    )

def list_patients(conn: DbConnection) -> None:
    """Display every patient.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Patients")
    print_table(patients_repository.list_all(conn), PATIENT_COLUMNS)

def search_patient(conn: DbConnection) -> None:
    """Display the patients whose first or last name contains the searched text.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Search a patient")
    term = ask_text("Name to search")
    print_table(patients_repository.search(conn, term), PATIENT_COLUMNS)

def add_patient(conn: DbConnection) -> None:
    """Create a patient.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Add a patient")
    patient = ask_patient()
    try:
        patient.id = patients_repository.create(conn, patient)
    except errors.UniqueViolation:
        print("A patient with this email already exists.")
        return
    print(f"Patient #{patient.id} {patient.full_name} created.")

def update_patient(conn: DbConnection) -> None:
    """Update a patient. Empty answers keep the current values.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Update a patient")
    patient = choose_patient(conn)
    if patient is None:
        return
    print("Press Enter to keep the value in brackets.")
    updated = ask_patient(patient)
    try:
        patients_repository.update(conn, updated)
    except errors.UniqueViolation:
        print("Another patient already uses this email.")
        return
    print(f"Patient #{updated.id} {updated.full_name} updated.")

def delete_patient(conn: DbConnection) -> None:
    """Delete a patient who has no consultation, after confirmation.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Delete a patient")
    patient = choose_patient(conn)
    if patient is None or patient.id is None:
        return
    if not ask_confirmation(f"Delete {patient.full_name} and their allergies?"):
        print("Deletion cancelled.")
        return
    try:
        patients_repository.delete(conn, patient.id)
    except errors.ForeignKeyViolation:
        print(f"{patient.full_name} has consultations and cannot be deleted: "
              "medical records must be kept.")
        return
    print(f"{patient.full_name} deleted.")

def show_patient_record(conn: DbConnection) -> None:
    """Display the full record of a patient.

    Identity, allergies, then every consultation with its prescriptions.
    Prescribed medications the patient is allergic to are flagged.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Patient record")
    patient = choose_patient(conn)
    if patient is None or patient.id is None:
        return
    allergies = allergic_to_repository.list_for_patient(conn, patient.id)
    consultations = consultations_repository.list_for_patient(conn, patient.id)

    prescriptions_by_consultation: defaultdict[int, list[Prescription]] = defaultdict(list)
    for line in prescriptions_repository.list_for_patient(conn, patient.id):
        prescriptions_by_consultation[line.consultation_id].append(line)
    allergic_medication_ids = {allergy.medication_id for allergy in allergies}

    print_title(f"{patient.last_name.upper()} {patient.first_name} (#{patient.id})")
    print(f"Born: {format_value(patient.birth_date)} ({patient.age} years)   Sex: {patient.sex}")
    print(f"Phone: {format_value(patient.phone)}   Email: {patient.email}")

    print("\nAllergies")
    print_table(allergies, [("medication", "Medication"), ("dosage", "Dosage"),
                            ("severity", "Severity")])

    print(f"\nConsultations ({len(consultations)})")
    if not consultations:
        print("No consultation.")
    for consultation in consultations:
        print(f"\n[{format_value(consultation.consultation_date)}] {consultation.reason}"
              f" - Dr {consultation.doctor} ({consultation.specialty})")
        if consultation.note:
            print(f"    Notes: {consultation.note}")
        for line in prescriptions_by_consultation[consultation.id]:
            warning = "  /!\\ ALLERGY" if line.medication_id in allergic_medication_ids else ""
            print(f"    - {line.medication} {line.dosage}: {line.instruction},"
                  f" {line.duration_days} days{warning}")
