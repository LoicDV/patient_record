"""Menu actions on consultations and prescriptions."""

from actions.pickers import choose_consultation, choose_doctor, choose_medication, choose_patient
from console import ask_confirmation, ask_datetime, ask_int, ask_text, print_title
from db import DbConnection
from models import MAX_DURATION_DAYS, Medication, Patient, PrescriptionDraft
from repositories import allergic_to_repository, consultations_repository, prescriptions_repository

def is_safe_to_prescribe(conn: DbConnection, patient_id: int, patient_name: str,
                         medication: Medication) -> bool:
    """Warn if the patient is allergic to the medication and ask whether to continue.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        patient_name (str): Name shown in the warning
        medication (Medication): Medication about to be prescribed

    Returns:
        bool: True if there is no allergy or the user confirms anyway
    """
    severity = allergic_to_repository.find_severity(conn, patient_id, medication.id)
    if severity is None:
        return True
    print(f"/!\\ WARNING: {patient_name} is allergic to {medication.label} "
          f"(severity: {severity.value}).")
    return ask_confirmation("Prescribe it anyway?")

def ask_prescription(conn: DbConnection, patient_id: int,
                     patient_name: str) -> PrescriptionDraft | None:
    """Ask for one prescription line, with an allergy check.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        patient_name (str): Name shown in the allergy warning

    Returns:
        PrescriptionDraft | None: The prescription to save, or None if cancelled
    """
    medication = choose_medication(conn)
    if medication is None:
        return None
    if not is_safe_to_prescribe(conn, patient_id, patient_name, medication):
        print("Prescription cancelled.")
        return None
    return PrescriptionDraft(
        medication_id=medication.id,
        instruction=ask_text("Instructions"),
        duration_days=ask_int("Duration (days)", min_value=1, max_value=MAX_DURATION_DAYS),
    )

def choose_saved_patient(conn: DbConnection) -> tuple[int, Patient] | None:
    """Let the user pick a patient, and return it with its ID.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        tuple[int, Patient] | None: (ID, patient), or None if cancelled
    """
    patient = choose_patient(conn)
    if patient is None or patient.id is None:
        return None
    return patient.id, patient

def add_consultation(conn: DbConnection) -> None:
    """Record a consultation and its prescriptions.

    Every answer is collected first, then everything is written in a single
    transaction: either the consultation and all its prescriptions are saved,
    or nothing is. No transaction stays open while waiting for the user.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Add a consultation")
    chosen = choose_saved_patient(conn)
    if chosen is None:
        return
    patient_id, patient = chosen
    print()
    doctor = choose_doctor(conn)
    if doctor is None:
        return
    consultation_date = ask_datetime("Date")
    reason = ask_text("Reason", max_length=200)
    note = ask_text("Notes (optional)", required=False)

    drafts: list[PrescriptionDraft] = []
    while ask_confirmation("Add a prescription to this consultation?"):
        draft = ask_prescription(conn, patient_id, patient.full_name)
        if draft is not None:
            drafts.append(draft)

    with conn.transaction():
        consultation_id = consultations_repository.create(
            conn, patient_id, doctor.id, consultation_date, reason, note
        )
        for draft in drafts:
            prescriptions_repository.create(conn, consultation_id, draft)

    print(f"Consultation #{consultation_id} recorded with {len(drafts)} prescription(s).")

def add_prescription(conn: DbConnection) -> None:
    """Add a prescription to an existing consultation.

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Add a prescription")
    chosen = choose_saved_patient(conn)
    if chosen is None:
        return
    patient_id, patient = chosen
    print()
    consultation = choose_consultation(conn, patient_id)
    if consultation is None:
        return
    print()
    draft = ask_prescription(conn, patient_id, patient.full_name)
    if draft is None:
        return
    prescription_id = prescriptions_repository.create(conn, consultation.id, draft)
    print(f"Prescription #{prescription_id} added to consultation #{consultation.id}.")
