from psycopg.rows import class_row

from db import DbConnection
from models import Allergy, Severity

def list_for_patient(conn: DbConnection, patient_id: int) -> list[Allergy]:
    """Return the allergies of a patient, the most severe first.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        list[Allergy]: The allergies, with the medication name and dosage
    """
    with conn.cursor(row_factory=class_row(Allergy)) as cursor:
        return cursor.execute(
            """
            SELECT m.id AS medication_id, m.name AS medication, m.dosage, a.severity
            FROM allergic_to a
            JOIN medications m ON m.id = a.medication_id
            WHERE a.patient_id = %s
            ORDER BY array_position(ARRAY['severe', 'moderate', 'mild'], a.severity::text), m.name
            """,
            (patient_id,),
        ).fetchall()

def find_severity(conn: DbConnection, patient_id: int, medication_id: int) -> Severity | None:
    """Return how severe the allergy of a patient to a medication is.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        medication_id (int): ID of the medication

    Returns:
        Severity | None: The severity, or None if the patient is not allergic
    """
    row = conn.execute(
        "SELECT severity FROM allergic_to WHERE patient_id = %s AND medication_id = %s",
        (patient_id, medication_id),
    ).fetchone()
    return Severity(row["severity"]) if row else None

def add(conn: DbConnection, patient_id: int, medication_id: int, severity: Severity) -> None:
    """Record that a patient is allergic to a medication.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        medication_id (int): ID of the medication
        severity (Severity): How severe the allergy is

    Raises:
        psycopg.errors.UniqueViolation: If this allergy is already recorded
    """
    conn.execute(
        "INSERT INTO allergic_to (patient_id, medication_id, severity) VALUES (%s, %s, %s)",
        (patient_id, medication_id, severity.value),
    )
