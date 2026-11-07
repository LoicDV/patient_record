from psycopg.rows import class_row

from db import DbConnection, fetch_required
from models import Patient

SELECT_PATIENTS = """
    SELECT id, first_name, last_name, birth_date, sex, phone, email
    FROM patients
"""

def escape_like(term: str) -> str:
    """Escape the LIKE wildcards so that '%' and '_' are searched literally.

    Args:
        term (str): Text typed by the user

    Returns:
        str: The text with '\\', '%' and '_' preceded by a backslash
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def list_all(conn: DbConnection) -> list[Patient]:
    """Return every patient, sorted by last name then first name.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[Patient]: The patients
    """
    with conn.cursor(row_factory=class_row(Patient)) as cursor:
        return cursor.execute(SELECT_PATIENTS + " ORDER BY last_name, first_name").fetchall()

def search(conn: DbConnection, term: str) -> list[Patient]:
    """Return the patients whose first or last name contains a text.

    The search is case-insensitive (ILIKE) and the text can appear anywhere
    in the name.

    Args:
        conn (DbConnection): Connection to the database
        term (str): Text to search for

    Returns:
        list[Patient]: The matching patients, sorted by name
    """
    query = SELECT_PATIENTS + """
        WHERE last_name ILIKE %(pattern)s OR first_name ILIKE %(pattern)s
        ORDER BY last_name, first_name
    """
    with conn.cursor(row_factory=class_row(Patient)) as cursor:
        return cursor.execute(query, {"pattern": f"%{escape_like(term)}%"}).fetchall()

def get_by_id(conn: DbConnection, patient_id: int) -> Patient | None:
    """Return one patient.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        Patient | None: The patient, or None if the ID does not exist
    """
    with conn.cursor(row_factory=class_row(Patient)) as cursor:
        return cursor.execute(SELECT_PATIENTS + " WHERE id = %s", (patient_id,)).fetchone()

def create(conn: DbConnection, patient: Patient) -> int:
    """Insert a new patient.

    Args:
        conn (DbConnection): Connection to the database
        patient (Patient): Patient to save; its id is ignored

    Raises:
        psycopg.errors.UniqueViolation: If the email is already used

    Returns:
        int: ID given to the patient by the database
    """
    cursor = conn.execute(
        """
        INSERT INTO patients (first_name, last_name, birth_date, sex, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (patient.first_name, patient.last_name, patient.birth_date,
         patient.sex, patient.phone, patient.email),
    )
    return fetch_required(cursor)["id"]

def update(conn: DbConnection, patient: Patient) -> bool:
    """Save every field of an existing patient and set updated_at to now.

    Args:
        conn (DbConnection): Connection to the database
        patient (Patient): Patient to save, with its id

    Raises:
        ValueError: If the patient has no id (it was never saved)
        psycopg.errors.UniqueViolation: If another patient uses the email

    Returns:
        bool: True if the patient was updated, False if the ID does not exist
    """
    if patient.id is None:
        raise ValueError("Cannot update a patient that was never saved")
    cursor = conn.execute(
        """
        UPDATE patients
        SET first_name = %s, last_name = %s, birth_date = %s,
            sex = %s, phone = %s, email = %s, updated_at = now()
        WHERE id = %s
        """,
        (patient.first_name, patient.last_name, patient.birth_date,
         patient.sex, patient.phone, patient.email, patient.id),
    )
    return cursor.rowcount == 1

def delete(conn: DbConnection, patient_id: int) -> bool:
    """Delete a patient and, by cascade, their allergies.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient to delete

    Raises:
        psycopg.errors.ForeignKeyViolation: If the patient has consultations
            (ON DELETE RESTRICT: medical records must be kept)

    Returns:
        bool: True if the patient was deleted, False if the ID does not exist
    """
    cursor = conn.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    return cursor.rowcount == 1
