from dataclasses import dataclass

@dataclass(frozen=True)
class Medication:
    """A medication of the catalogue.

    Attributes:
        id (int): Database ID
        name (str): Name of the medication
        dosage (str): Dosage, e.g. '500 mg'
    """

    id: int
    name: str
    dosage: str

    @property
    def label(self) -> str:
        """str: Name followed by dosage, e.g. 'Paracetamol 1 g'."""
        return f"{self.name} {self.dosage}"
