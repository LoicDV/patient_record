from psycopg.rows import DictRow

from db import DbConnection, fetch_required

def list_for_patient(conn: DbConnection, patient_id: int) -> list[DictRow]:
    """Return every prescription of a patient, across all their consultations.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        list[DictRow]: The prescriptions, with the medication name and dosage
    """
    return conn.execute(
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

def create(
    conn: DbConnection,
    consultation_id: int,
    medication_id: int,
    instruction: str,
    duration_days: int,
) -> int:
    """Insert a prescription line.

    Args:
        conn (DbConnection): Connection to the database
        consultation_id (int): ID of the consultation
        medication_id (int): ID of the prescribed medication
        instruction (str): Posology, e.g. '1 tablet 3 times a day'
        duration_days (int): Duration of the treatment, strictly positive

    Returns:
        int: ID of the new prescription
    """
    cursor = conn.execute(
        """
        INSERT INTO prescriptions (consultation_id, medication_id, instruction, duration_days)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (consultation_id, medication_id, instruction, duration_days),
    )
    return fetch_required(cursor)["id"]
