from psycopg.rows import DictRow

from db import DbConnection

def list_all(conn: DbConnection) -> list[DictRow]:
    """Return every doctor with the name of their specialty.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: The doctors, sorted by specialty then by name
    """
    return conn.execute(
        """
        SELECT d.id, d.last_name, d.first_name, s.name AS specialty
        FROM doctors d
        JOIN specialties s ON s.id = d.specialty_id
        ORDER BY s.name, d.last_name, d.first_name
        """
    ).fetchall()
