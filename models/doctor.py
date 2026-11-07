from dataclasses import dataclass

@dataclass(frozen=True)
class Doctor:
    """A doctor with the name of their specialty (joined from specialties).

    Attributes:
        id (int): Database ID
        first_name (str): First name
        last_name (str): Last name
        specialty (str): Name of the specialty
    """

    id: int
    first_name: str
    last_name: str
    specialty: str

    @property
    def full_name(self) -> str:
        """str: First name followed by last name."""
        return f"{self.first_name} {self.last_name}"
