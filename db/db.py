from psycopg import Connection, connect
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

SQL_DIR = Path(__file__).parent

def init_db(conn: Connection) -> None:
    sql = Path(SQL_DIR, "schema.sql").read_text(encoding="UTF-8")
    conn.execute(sql)

    sql = Path(SQL_DIR, "seed.sql").read_text(encoding="UTF-8")
    conn.execute(sql)

def get_connection() -> Connection:
    return connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        autocommit=True
    )