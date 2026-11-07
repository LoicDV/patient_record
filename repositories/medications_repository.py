from psycopg.rows import DictRow

from db import DbConnection

def list_all(conn: DbConnection) -> list[DictRow]:
    """Return every medication of the catalogue.

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        list[DictRow]: The medications, sorted by name then by dosage
    """
    return conn.execute(
        "SELECT id, name, dosage FROM medications ORDER BY name, dosage"
    ).fetchall()
