import os
from pathlib import Path

from psycopg import Connection, connect
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

SQL_DIR = Path(__file__).parent
REQUIRED_SETTINGS = ("DB_NAME", "DB_USER", "DB_HOST", "DB_PORT")

def init_db(conn: Connection) -> None:
    """Initialize all tables in the database. Use the 'schema.sql' in the 'db'
    folder to build these tables

    Args:
        conn (Connection): Connection to the database
    """
    run_sql_file(conn, "schema.sql")

def seed_db(conn: Connection) -> None:
    """Insert fake data in the database. Use the 'seed.sql' in the 'db' folder
    to complete these tables

    Args:
        conn (Connection): Connection to the database
    """
    run_sql_file(conn, "seed.sql")

def run_sql_file(conn: Connection, filename: str) -> None:
    """Execute sql file by the connection to the database. Use inside 'init_db'
    and 'seed_db'

    Args:
        conn (Connection): Connection to the database
        filename (str): Name of the sql file
    """
    sql = (SQL_DIR / filename).read_text(encoding="UTF-8")
    conn.execute(sql)

def database_exists(conn: Connection) -> bool:
    """Check whether the tables exist in the database

    Args:
        conn (Connection): Connection to the database

    Returns:
        bool: True if the 'patients' table exists, False otherwise
    """
    res = conn.execute("SELECT to_regclass('patients') IS NOT NULL AS found").fetchone()
    return res["found"]

def get_connection() -> Connection:
    """Get the connection to the database. Use .env to get informations to
    connect to the database.

    Raises:
        RuntimeError: If missing settings from .env file

    Returns:
        Connection: Connection to the database
    """
    missing = [name for name in REQUIRED_SETTINGS if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing settings in .env: {', '.join(missing)}")

    return connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        autocommit=True,
        row_factory=dict_row,
    )
