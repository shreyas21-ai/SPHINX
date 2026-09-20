from typing import Dict, Any
from app.models.role import Role


class PrivacyMasker:
    """
    Role-Based Privacy Exposure Engine.
    Filters and redacts sensitive patient health information (PHI) fields
    according to strict role-based access rules.
    """

    REDACTED_TEXT = "[REDACTED_PRIVACY_POLICY]"

    @classmethod
    def mask_patient_data(cls, patient_dict: Dict[str, Any], role_name: str) -> Dict[str, Any]:
        """Masks patient entity attributes based on caller role."""
        if not patient_dict:
            return {}

        masked = dict(patient_dict)

        if role_name in (Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST):
            # These roles are allowed full demographic access
            return masked

        if role_name == Role.INSURANCE_OFFICER:
            # Insurance officers see insurance details, policy number, name; clinical address/dob are redacted
            masked['dob'] = cls.REDACTED_TEXT
            masked['address'] = cls.REDACTED_TEXT

        return masked

    @classmethod
    def mask_medical_record(cls, record_dict: Dict[str, Any], role_name: str) -> Dict[str, Any]:
        """
        Masks medical record clinical fields based on role:
        - DOCTOR: Full Record
        - NURSE: Vitals, Prescription/Medicines, Allergies, Doctor Notes (Masked: Disease, Diagnosis, History, Insurance Details)
        - RECEPTIONIST: Redacts ALL clinical records
        - INSURANCE_OFFICER: Insurance Details, Treatment Plan summary (Masked: Disease, Diagnosis, Notes, Lab Reports, Vitals)
        - ADMIN: Redacts ALL clinical records (Admin manages system, not health records)
        """
        if not record_dict:
            return {}

        masked = dict(record_dict)

        if role_name == Role.DOCTOR:
            # Doctor gets full authorized clinical exposure
            return masked

        if role_name == Role.NURSE:
            # Nurse gets vitals, prescription/medicines, allergies, treatment_plan/care info
            # Nurse must NOT automatically see doctor notes, diagnosis, history, lab reports, insurance details
            masked['disease'] = cls.REDACTED_TEXT
            masked['diagnosis'] = cls.REDACTED_TEXT
            masked['medical_history'] = cls.REDACTED_TEXT
            masked['doctor_notes'] = cls.REDACTED_TEXT
            masked['lab_reports'] = cls.REDACTED_TEXT
            masked['insurance_details'] = cls.REDACTED_TEXT
            return masked

        if role_name == Role.INSURANCE_OFFICER:
            # Insurance Officer gets claim-relevant diagnosis (disease), treatment procedure (treatment_plan), insurance_details
            # Insurance Officer must NOT see doctor notes, lab_reports, complete prescriptions, history, vitals, allergies
            masked['diagnosis'] = cls.REDACTED_TEXT
            masked['medical_history'] = cls.REDACTED_TEXT
            masked['prescription'] = cls.REDACTED_TEXT
            masked['lab_reports'] = cls.REDACTED_TEXT
            masked['doctor_notes'] = cls.REDACTED_TEXT
            masked['vitals'] = cls.REDACTED_TEXT
            masked['allergies'] = cls.REDACTED_TEXT
            return masked

        if role_name in (Role.RECEPTIONIST, Role.ADMIN):
            # Receptionist & Admin get zero clinical details
            masked['disease'] = cls.REDACTED_TEXT
            masked['diagnosis'] = cls.REDACTED_TEXT
            masked['medical_history'] = cls.REDACTED_TEXT
            masked['prescription'] = cls.REDACTED_TEXT
            masked['lab_reports'] = cls.REDACTED_TEXT
            masked['doctor_notes'] = cls.REDACTED_TEXT
            masked['insurance_details'] = cls.REDACTED_TEXT
            masked['treatment_plan'] = cls.REDACTED_TEXT
            masked['allergies'] = cls.REDACTED_TEXT
            masked['vitals'] = cls.REDACTED_TEXT

        return masked
