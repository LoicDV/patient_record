from psycopg.rows import DictRow

from db import DbConnection

def consultations_per_doctor(conn: DbConnection) -> list[DictRow]:
    """Number of consultations per doctor, doctors without any included (LEFT JOIN)

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT d.last_name, d.first_name, s.name AS specialty,
               COUNT(c.id) AS consultations
        FROM doctors d
        JOIN specialties s ON s.id = d.specialty_id
        LEFT JOIN consultations c ON c.doctor_id = d.id
        GROUP BY d.id, s.name
        ORDER BY consultations DESC, d.last_name
        """
    ).fetchall()

def consultations_per_specialty(conn: DbConnection) -> list[DictRow]:
    """Number of doctors and consultations per specialty, across three tables

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT s.name AS specialty,
               COUNT(DISTINCT d.id) AS doctors,
               COUNT(c.id) AS consultations
        FROM specialties s
        LEFT JOIN doctors d ON d.specialty_id = s.id
        LEFT JOIN consultations c ON c.doctor_id = d.id
        GROUP BY s.id
        ORDER BY consultations DESC, s.name
        """
    ).fetchall()

def consultations_per_month(conn: DbConnection) -> list[DictRow]:
    """Number of consultations and distinct patients per month

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT to_char(date_trunc('month', consultation_date), 'YYYY-MM') AS month,
               COUNT(*) AS consultations,
               COUNT(DISTINCT patient_id) AS patients
        FROM consultations
        GROUP BY date_trunc('month', consultation_date)
        ORDER BY date_trunc('month', consultation_date)
        """
    ).fetchall()

def most_prescribed_medications(conn: DbConnection, limit: int = 5) -> list[DictRow]:
    """The most prescribed medications, with the number of distinct patients

    Args:
        conn (DbConnection): Connection to the database
        limit (int, optional): Maximum number of rows
            Defaults to 5

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT m.name, m.dosage,
               COUNT(p.id) AS prescriptions,
               COUNT(DISTINCT c.patient_id) AS patients
        FROM medications m
        LEFT JOIN prescriptions p ON p.medication_id = m.id
        LEFT JOIN consultations c ON c.id = p.consultation_id
        GROUP BY m.id
        ORDER BY prescriptions DESC, m.name
        LIMIT %s
        """,
        (limit,),
    ).fetchall()

def patients_without_consultation(conn: DbConnection) -> list[DictRow]:
    """Patients who never had a consultation (anti-join with LEFT JOIN ... IS NULL)

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT p.id, p.last_name, p.first_name, p.email, p.created_at
        FROM patients p
        LEFT JOIN consultations c ON c.patient_id = p.id
        WHERE c.id IS NULL
        ORDER BY p.last_name, p.first_name
        """
    ).fetchall()

def allergy_alerts(conn: DbConnection) -> list[DictRow]:
    """Prescriptions of a medication the patient is allergic to

    allergic_to is joined on two columns, both reached through different paths:
    the patient through the consultation, the medication through the prescription

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT c.consultation_date,
               pa.last_name, pa.first_name,
               m.name AS medication, m.dosage,
               a.severity,
               d.last_name AS doctor
        FROM prescriptions pr
        JOIN consultations c ON c.id = pr.consultation_id
        JOIN patients pa     ON pa.id = c.patient_id
        JOIN medications m   ON m.id = pr.medication_id
        JOIN doctors d       ON d.id = c.doctor_id
        JOIN allergic_to a   ON a.patient_id = c.patient_id
                            AND a.medication_id = pr.medication_id
        ORDER BY array_position(ARRAY['severe', 'moderate', 'mild'], a.severity::text),
                 c.consultation_date DESC
        """
    ).fetchall()

def last_consultation_per_patient(conn: DbConnection) -> list[DictRow]:
    """Latest consultation of each patient, using PostgreSQL's DISTINCT ON

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: One dictionary per result row
    """
    return conn.execute(
        """
        SELECT *
        FROM (
            SELECT DISTINCT ON (p.id)
                   p.last_name, p.first_name, c.consultation_date, c.reason,
                   d.last_name AS doctor
            FROM patients p
            JOIN consultations c ON c.patient_id = p.id
            JOIN doctors d ON d.id = c.doctor_id
            ORDER BY p.id, c.consultation_date DESC
        ) AS latest
        ORDER BY consultation_date DESC
        """
    ).fetchall()
