import os
from pathlib import Path

from psycopg import Connection, Cursor
from psycopg.rows import DictRow, dict_row
from dotenv import load_dotenv

load_dotenv()

SQL_DIR = Path(__file__).parent
REQUIRED_SETTINGS = ("DB_NAME", "DB_USER", "DB_HOST", "DB_PORT")

DbConnection = Connection[DictRow]

def init_db(conn : DbConnection) -> None:
    """Initialize all tables in the database. Use the 'schema.sql' in the 'db'
    folder to build these tables

    Args:
        conn (DbConnection): Connection to the database
    """
    run_sql_file(conn, "schema.sql")

def seed_db(conn : DbConnection) -> None:
    """Insert fake data in the database. Use the 'seed.sql' in the 'db' folder
    to complete these tables

    Args:
        conn (DbConnection): Connection to the database
    """
    run_sql_file(conn, "seed.sql")

def run_sql_file(conn : DbConnection, filename: str) -> None:
    """Execute sql file by the connection to the database. Use inside 'init_db'
    and 'seed_db'

    Args:
        conn (DbConnection): Connection to the database
        filename (str): Name of the sql file
    """
    sql = (SQL_DIR / filename).read_bytes()
    conn.execute(sql)

def database_exists(conn : DbConnection) -> bool:
    """Check whether the tables exist in the database

    Args:
        conn (DbConnection): Connection to the database

    Returns:
        bool: True if the 'patients' table exists, False otherwise
    """
    cursor = conn.execute("SELECT to_regclass('patients') IS NOT NULL AS found")
    return fetch_required(cursor)["found"]

def fetch_required(cursor: Cursor[DictRow]) -> DictRow:
    """Return the next row of a query that always produces one

    Used for 'INSERT ... RETURNING' and aggregates, which always return a row
    fetchone() is typed 'DictRow | None', so this helper makes the guarantee
    explicit for type checkers instead of repeating a None check everywhere

    Args:
        cursor (Cursor[DictRow]): Cursor of the executed query

    Raises:
        RuntimeError: If the query unexpectedly returned no row

    Returns:
        DictRow: The row, as a dictionary
    """
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("The query returned no row")
    return row

def get_connection() -> DbConnection:
    """Get the connection to the database. Use .env to get informations to
    connect to the database.

    Raises:
        RuntimeError: If missing settings from .env file

    Returns:
        DbConnection: Connection to the database
    """
    missing = [name for name in REQUIRED_SETTINGS if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing settings in .env: {', '.join(missing)}")

    return DbConnection.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        autocommit=True,
        row_factory=dict_row,
    )
