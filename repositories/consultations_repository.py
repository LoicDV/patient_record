from datetime import datetime

from psycopg.rows import DictRow

from db import DbConnection, fetch_required

def list_for_patient(conn: DbConnection, patient_id: int) -> list[DictRow]:
    """Return the consultations of a patient, the latest first.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        list[DictRow]: The consultations, with the doctor's name and specialty
    """
    return conn.execute(
        """
        SELECT c.id, c.consultation_date, c.reason, c.note,
               d.first_name || ' ' || d.last_name AS doctor,
               s.name AS specialty
        FROM consultations c
        JOIN doctors d ON d.id = c.doctor_id
        JOIN specialties s ON s.id = d.specialty_id
        WHERE c.patient_id = %s
        ORDER BY c.consultation_date DESC
        """,
        (patient_id,),
    ).fetchall()

def create(
    conn: DbConnection,
    patient_id: int,
    doctor_id: int,
    consultation_date: datetime,
    reason: str,
    note: str | None,
) -> int:
    """Insert a consultation.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient
        doctor_id (int): ID of the doctor
        consultation_date (datetime): Date and time of the consultation
        reason (str): Reason for the consultation
        note (str | None): Free notes, optional

    Returns:
        int: ID of the new consultation
    """
    cursor = conn.execute(
        """
        INSERT INTO consultations (patient_id, doctor_id, consultation_date, reason, note)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (patient_id, doctor_id, consultation_date, reason, note),
    )
    return fetch_required(cursor)["id"]
