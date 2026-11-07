from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    """Severity of an allergy. The values are the ones stored in the database
    """

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

    @classmethod
    def values(cls) -> list[str]:
        """Return every severity as stored in the database.

        Returns:
            list[str]: ['mild', 'moderate', 'severe']
        """
        return [severity.value for severity in cls]


@dataclass(frozen=True)
class Allergy:
    """An allergy of a patient to a medication (joined from medications)

    Attributes:
        medication_id (int): ID of the medication
        medication (str): Name of the medication
        dosage (str): Dosage of the medication
        severity (Severity): How severe the allergy is
    """

    medication_id: int
    medication: str
    dosage: str
    severity: Severity

    def __post_init__(self) -> None:
        """Convert the severity read from the database ('mild'...) into a Severity

        frozen=True forbids normal assignment, hence object.__setattr__

        Raises:
            ValueError: If the severity is unknown
        """
        object.__setattr__(self, "severity", Severity(self.severity))
