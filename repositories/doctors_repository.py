from psycopg.rows import class_row

from db import DbConnection
from models import Doctor

def list_all(conn: DbConnection) -> list[Doctor]:
    """Return every doctor with the name of their specialty.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[Doctor]: The doctors, sorted by specialty then by name
    """
    with conn.cursor(row_factory=class_row(Doctor)) as cursor:
        return cursor.execute(
            """
            SELECT d.id, d.first_name, d.last_name, s.name AS specialty
            FROM doctors d
            JOIN specialties s ON s.id = d.specialty_id
            ORDER BY s.name, d.last_name, d.first_name
            """
        ).fetchall()
