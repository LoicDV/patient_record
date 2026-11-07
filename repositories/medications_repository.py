from psycopg.rows import class_row

from db import DbConnection
from models import Medication

def list_all(conn: DbConnection) -> list[Medication]:
    """Return every medication of the catalogue.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[Medication]: The medications, sorted by name then by dosage
    """
    with conn.cursor(row_factory=class_row(Medication)) as cursor:
        return cursor.execute(
            "SELECT id, name, dosage FROM medications ORDER BY name, dosage"
        ).fetchall()
