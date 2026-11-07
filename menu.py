from collections.abc import Callable

from psycopg import errors, Error, OperationalError
from actions import patient_actions, allergy_actions, consultation_actions
from db import init_db, seed_db, DbConnection
from console import ask_confirmation, print_title

Action = Callable[[DbConnection], None]

def not_implemented(conn: DbConnection) -> None:
    """Placeholder for the options that are not developed yet

    Args:
        conn (DbConnection): Connection to the database
    """
    print("Not implemented")

def run_action(conn: DbConnection, action: Action) -> None:
    """Run an action and report database errors without leaving the menu

    Args:
        conn (DbConnection): Connection to the database
        action (Action): Action choose by the user
    """
    try:
        action(conn)
    except OperationalError:
        raise  # Done in main.py
    except errors.UniqueViolation as error:
        print(f"Error: this record already exists ({error.diag.constraint_name})")
    except errors.ForeignKeyViolation as error:
        print(f"Error: operation refused, the record is linked to others "
              f"({error.diag.constraint_name})")
    except errors.CheckViolation as error:
        print(f"Error: invalid value ({error.diag.constraint_name})")
    except Error as error: # Default error
        print(f"Database error: {error}")

def show_statistics(conn: DbConnection) -> None:
    """Open the statistics submenu

    Args:
        conn (DbConnection): Connection to the database
    """
    run_options_menu(conn, "Statistics", MENU_STAT, "Back")

def run_options_menu(conn: DbConnection,
                     title: str,
                     options: dict[str, tuple[str, Action]],
                     exit_label: str) -> None:
    """Display a menu in a loop and run the chosen action until the user types 0

    Args:
        conn (DbConnection): Connection to the database
        title (str): Title displayed above the options
        options (dict[str, tuple[str, Action]]): Choice -> (label, action)
        exit_label (str): Label of the 0 option
    """
    while True:
        print_title(title)
        for key, (label, _) in options.items():
            print(f"{key:>3}. {label}")
        print(f"{'0':>3}. {exit_label}")

        choice = input("Your choice: ").strip()
        if choice == "0":
            return
        if choice not in options:
            print("Invalid choice, please try again")
            continue
        _, action = options[choice]
        run_action(conn, action)

def reset_database(conn: DbConnection) -> None:
    """Rebuild the tables and reload the test data, after confirmation

    Args:
        conn (DbConnection): Connection to the database
    """
    if ask_confirmation("Are you sure you want to reset the database ?\n"
                     "You will lose all your data"):
        init_db(conn)
        seed_db(conn)

MENU = {
    "1"  :  ("List patients", patient_actions.list_patients),
    "2"  :  ("Search a patient", patient_actions.search_patient),
    "3"  :  ("Show a patient’s record", patient_actions.show_patient_record),
    "4"  :  ("Add a patient", patient_actions.add_patient),
    "5"  :  ("Update a patient", patient_actions.update_patient),
    "6"  :  ("Delete a patient", patient_actions.delete_patient),
    "7"  :  ("Add a consultation", consultation_actions.add_consultation),
    "8"  :  ("Add a prescription", consultation_actions.add_prescription),
    "9"  :  ("Add an allergy", allergy_actions.add_allergy),
    "10" :  ("Statistics", show_statistics),
    "11" :  ("Reset database", reset_database),
}

MENU_STAT = {
    "1" : ("Consultations per doctor", not_implemented),
    "2" : ("Consultations per specialty", not_implemented),
    "3" : ("Most prescribed medications", not_implemented),
    "4" : ("Patients without consultation", not_implemented),
    "5" : ("Allergy alerts", not_implemented),
    "6" : ("Last consultation per patient", not_implemented),
}

def run_menu(conn: DbConnection) -> None:
    """Print the menu options and dispatch to the action

    Args:
        conn (DbConnection): Connection to the database
    """
    run_options_menu(conn, "Patient records", MENU, "Exit")
