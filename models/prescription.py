from dataclasses import dataclass

MAX_DURATION_DAYS = 32767

@dataclass(frozen=True)
class Prescription:
    """A saved prescription line, with the medication joined.

    Attributes:
        consultation_id (int): ID of the consultation
        medication_id (int): ID of the medication
        medication (str): Name of the medication
        dosage (str): Dosage of the medication
        instruction (str): Posology, e.g. '1 tablet 3 times a day'
        duration_days (int): Duration of the treatment
    """

    consultation_id: int
    medication_id: int
    medication: str
    dosage: str
    instruction: str
    duration_days: int


@dataclass(frozen=True)
class PrescriptionDraft:
    """A prescription line typed by the user, not saved yet.

    Kept apart from Prescription because it has no consultation yet: the
    consultation and its prescriptions are saved together in one transaction.

    Attributes:
        medication_id (int): ID of the prescribed medication
        instruction (str): Posology
        duration_days (int): Duration of the treatment, strictly positive
    """

    medication_id: int
    instruction: str
    duration_days: int

    def __post_init__(self) -> None:
        """Validate the duration, as the database CHECK constraint does.

        Raises:
            ValueError: If the duration is not between 1 and MAX_DURATION_DAYS
        """
        if not 1 <= self.duration_days <= MAX_DURATION_DAYS:
            raise ValueError(f"The duration must be between 1 and {MAX_DURATION_DAYS} days")
