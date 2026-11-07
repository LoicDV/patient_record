from dataclasses import dataclass
from datetime import date

SEXES = ("M", "F", "X")

@dataclass
class Patient:
    """A patient, as stored in the patients table.

    Attributes:
        first_name (str): First name
        last_name (str): Last name
        birth_date (date): Date of birth
        sex (str): One of SEXES
        email (str): Email address, unique among patients
        phone (str | None): Phone number, optional
        id (int | None): Database ID, None until the patient is saved
    """

    first_name: str
    last_name: str
    birth_date: date
    sex: str
    email: str
    phone: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        """Validate the fields that the database also checks.

        Raises:
            ValueError: If the sex is unknown or the birth date is in the future
        """
        if self.sex not in SEXES:
            raise ValueError(f"Sex must be one of {', '.join(SEXES)}, not {self.sex!r}")
        if self.birth_date > date.today():
            raise ValueError("The birth date cannot be in the future")

    @property
    def full_name(self) -> str:
        """str: First name followed by last name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """int: Age in full years today."""
        return self.age_on(date.today())

    def age_on(self, day: date) -> int:
        """Return the age of the patient on a given day.

        Args:
            day (date): Day at which the age is computed

        Returns:
            int: Number of full years since the birth date
        """
        birthday_not_reached = (day.month, day.day) < (self.birth_date.month, self.birth_date.day)
        return day.year - self.birth_date.year - birthday_not_reached
