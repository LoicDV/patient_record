import sys

from psycopg import OperationalError

from db import get_connection, database_exists, init_db, seed_db
from menu import run_menu

def main() -> None:
    """Launch for the application
    """
    try:
        with get_connection() as conn:
            if not database_exists(conn):
                print("No database found. Creating it...")
                init_db(conn)
                seed_db(conn)
                print("Database created and filled with test data.")
            run_menu(conn)
    except (KeyboardInterrupt, EOFError):
        print("Exiting the application. Good bye!")
    except (OperationalError, RuntimeError):
        print("Unable to connect to the database. Check that PostgreSQL is"
                "running and that your .env settings are correct.")
        sys.exit(1)

if __name__ == "__main__":
    main()
