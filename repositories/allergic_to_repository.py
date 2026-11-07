from psycopg.rows import DictRow

from db import DbConnection

SEVERITIES = ("mild", "moderate", "severe")

def list_for_patient(conn: DbConnection, patient_id: int) -> list[DictRow]:
    """Return the allergies of a patient, the most severe first.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        list[DictRow]: The allergies, with the medication name and dosage
    """
    return conn.execute(
        """
        SELECT m.id AS medication_id, m.name AS medication, m.dosage, a.severity
        FROM allergic_to a
        JOIN medications m ON m.id = a.medication_id
        WHERE a.patient_id = %s
        ORDER BY array_position(ARRAY['severe', 'moderate', 'mild'], a.severity::text), m.name
        """,
        (patient_id,),
    ).fetchall()

def find(conn: DbConnection, patient_id: int, medication_id: int) -> DictRow | None:
    """Return the allergy of a patient to a medication.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        medication_id (int): ID of the medication

    Returns:
        DictRow | None: The allergy (with its severity), or None if there is none
    """
    return conn.execute(
        "SELECT severity FROM allergic_to WHERE patient_id = %s AND medication_id = %s",
        (patient_id, medication_id),
    ).fetchone()

def add(conn: DbConnection, patient_id: int, medication_id: int, severity: str) -> None:
    """Record that a patient is allergic to a medication.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        medication_id (int): ID of the medication
        severity (str): One of SEVERITIES

    Raises:
        psycopg.errors.UniqueViolation: If this allergy is already recorded
    """
    conn.execute(
        "INSERT INTO allergic_to (patient_id, medication_id, severity) VALUES (%s, %s, %s)",
        (patient_id, medication_id, severity),
    )
