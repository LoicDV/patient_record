from console import print_table, print_title
from db import DbConnection
from repositories import stats_repository

def consultations_per_doctor(conn: DbConnection) -> None:
    """Display the consultations per doctor

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Consultations per doctor")
    print_table(stats_repository.consultations_per_doctor(conn), [
        ("last_name", "Last name"), ("first_name", "First name"),
        ("specialty", "Specialty"), ("consultations", "Consultations"),
    ])

def consultations_per_specialty(conn: DbConnection) -> None:
    """Display the consultations per specialty

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Consultations per specialty")
    print_table(stats_repository.consultations_per_specialty(conn), [
        ("specialty", "Specialty"), ("doctors", "Doctors"), ("consultations", "Consultations"),
    ])

def consultations_per_month(conn: DbConnection) -> None:
    """Display the consultations per month

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Consultations per month")
    print_table(stats_repository.consultations_per_month(conn), [
        ("month", "Month"), ("consultations", "Consultations"), ("patients", "Patients"),
    ])

def most_prescribed_medications(conn: DbConnection) -> None:
    """Display the most prescribed medications

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Most prescribed medications")
    print_table(stats_repository.most_prescribed_medications(conn), [
        ("name", "Medication"), ("dosage", "Dosage"),
        ("prescriptions", "Prescriptions"), ("patients", "Patients"),
    ])

def patients_without_consultation(conn: DbConnection) -> None:
    """Display the patients without consultation

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Patients without consultation")
    print_table(stats_repository.patients_without_consultation(conn), [
        ("id", "ID"), ("last_name", "Last name"), ("first_name", "First name"),
        ("email", "Email"), ("created_at", "Registered on"),
    ])

def allergy_alerts(conn: DbConnection) -> None:
    """Display the allergy alerts

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Allergy alerts")
    print_table(stats_repository.allergy_alerts(conn), [
        ("consultation_date", "Date"), ("last_name", "Last name"), ("first_name", "First name"),
        ("medication", "Medication"), ("dosage", "Dosage"), ("severity", "Severity"),
        ("doctor", "Doctor"),
    ])

def last_consultation_per_patient(conn: DbConnection) -> None:
    """Display the last consultation per patient

    Args:
        conn (DbConnection): Connection to the database
    """
    print_title("Last consultation per patient")
    print_table(stats_repository.last_consultation_per_patient(conn), [
        ("last_name", "Last name"), ("first_name", "First name"),
        ("consultation_date", "Date"), ("reason", "Reason"), ("doctor", "Doctor"),
    ])
