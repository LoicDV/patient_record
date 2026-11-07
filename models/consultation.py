from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Consultation:
    """A consultation with the doctor's name and specialty (joined).

    Attributes:
        id (int): Database ID
        consultation_date (datetime): Date and time of the consultation
        reason (str): Reason for the consultation
        note (str | None): Free notes
        doctor (str): Full name of the doctor
        specialty (str): Specialty of the doctor
    """

    id: int
    consultation_date: datetime
    reason: str
    note: str | None
    doctor: str
    specialty: str
