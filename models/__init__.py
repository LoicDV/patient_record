from .allergy import Allergy, Severity
from .consultation import Consultation
from .doctor import Doctor
from .medication import Medication
from .patient import SEXES, Patient
from .prescription import MAX_DURATION_DAYS, Prescription, PrescriptionDraft

__all__ = ["MAX_DURATION_DAYS",
           "SEXES",
           "Allergy",
           "Consultation",
           "Doctor",
           "Medication",
           "Patient",
           "Prescription",
           "PrescriptionDraft",
           "Severity"
]