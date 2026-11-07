from psycopg.rows import class_row

from db import DbConnection, fetch_required
from models import Prescription, PrescriptionDraft

def list_for_patient(conn: DbConnection, patient_id: int) -> list[Prescription]:
    """Return every prescription of a patient, across all their consultations.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        list[Prescription]: The prescriptions, with the medication name and dosage
    """
    with conn.cursor(row_factory=class_row(Prescription)) as cursor:
        return cursor.execute(
            """
            SELECT p.consultation_id, p.medication_id, m.name AS medication, m.dosage,
                   p.instruction, p.duration_days
            FROM prescriptions p
            JOIN consultations c ON c.id = p.consultation_id
            JOIN medications m ON m.id = p.medication_id
            WHERE c.patient_id = %s
            ORDER BY p.id
            """,
            (patient_id,),
        ).fetchall()

def create(conn: DbConnection, consultation_id: int, draft: PrescriptionDraft) -> int:
    """Save a prescription line in a consultation.

    Args:
        conn (DbConnection): Connection to the database
        consultation_id (int): ID of the consultation
        draft (PrescriptionDraft): Medication, posology and duration

    Returns:
        int: ID of the new prescription
    """
    cursor = conn.execute(
        """
        INSERT INTO prescriptions (consultation_id, medication_id, instruction, duration_days)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (consultation_id, draft.medication_id, draft.instruction, draft.duration_days),
    )
    return fetch_required(cursor)["id"]
