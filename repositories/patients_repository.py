from datetime import date

from psycopg.rows import DictRow

from db import DbConnection, fetch_required

SELECT_PATIENTS = """
    SELECT id, last_name, first_name, birth_date,
           date_part('year', age(birth_date))::int AS age,
           sex, phone, email
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

def list_all(conn: DbConnection) -> list[DictRow]:
    """Return every patient, sorted by last name then first name.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: The patients, with their age computed by PostgreSQL
    """
    return conn.execute(SELECT_PATIENTS + " ORDER BY last_name, first_name").fetchall()

def search(conn: DbConnection, term: str) -> list[DictRow]:
    """Return the patients whose first or last name contains a text.

    The search is case-insensitive (ILIKE) and the text can appear anywhere
    in the name.

    Args:
        conn (DbConnection): Connection to the database
        term (str): Text to search for

    Returns:
        list[DictRow]: The matching patients, sorted by name
    """
    query = SELECT_PATIENTS + """
        WHERE last_name ILIKE %(pattern)s OR first_name ILIKE %(pattern)s
        ORDER BY last_name, first_name
    """
    return conn.execute(query, {"pattern": f"%{escape_like(term)}%"}).fetchall()

def get_by_id(conn: DbConnection, patient_id: int) -> DictRow | None:
    """Return one patient.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient

    Returns:
        DictRow | None: The patient, or None if the ID does not exist
    """
    return conn.execute(SELECT_PATIENTS + " WHERE id = %s", (patient_id,)).fetchone()

def create(
    conn: DbConnection,
    first_name: str,
    last_name: str,
    birth_date: date,
    sex: str,
    phone: str | None,
    email: str,
) -> int:
    """Insert a patient.

    Args:
        conn (DbConnection): Connection to the database
        first_name (str): First name
        last_name (str): Last name
        birth_date (date): Date of birth, not in the future
        sex (str): 'M', 'F' or 'X'
        phone (str | None): Phone number, optional
        email (str): Email address, unique among patients

    Raises:
        psycopg.errors.UniqueViolation: If the email is already used

    Returns:
        int: ID of the new patient
    """
    cursor = conn.execute(
        """
        INSERT INTO patients (first_name, last_name, birth_date, sex, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (first_name, last_name, birth_date, sex, phone, email),
    )
    return fetch_required(cursor)["id"]

def update(
    conn: DbConnection,
    patient_id: int,
    first_name: str,
    last_name: str,
    birth_date: date,
    sex: str,
    phone: str | None,
    email: str,
) -> bool:
    """Update every field of a patient and set updated_at to now.

    Args:
        conn (DbConnection): Connection to the database
        patient_id (int): ID of the patient to update
        first_name (str): First name
        last_name (str): Last name
        birth_date (date): Date of birth, not in the future
        sex (str): 'M', 'F' or 'X'
        phone (str | None): Phone number, optional
        email (str): Email address, unique among patients

    Raises:
        psycopg.errors.UniqueViolation: If another patient uses the email

    Returns:
        bool: True if the patient was updated, False if the ID does not exist
    """
    cursor = conn.execute(
        """
        UPDATE patients
        SET first_name = %s, last_name = %s, birth_date = %s,
            sex = %s, phone = %s, email = %s, updated_at = now()
        WHERE id = %s
        """,
        (first_name, last_name, birth_date, sex, phone, email, patient_id),
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
