from typing import Optional, List, Set
from app.extensions import db
from app.models.patient import Patient


class PatientRepository:
    @staticmethod
    def get_by_id(patient_id: int) -> Optional[Patient]:
        return Patient.query.get(patient_id)

    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[Patient]:
        return Patient.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_all(page: int = 1, per_page: int = 50) -> List[Patient]:
        return Patient.query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False).items

    @staticmethod
    def get_by_ids(patient_ids: List[int]) -> List[Patient]:
        if not patient_ids:
            return []
        return Patient.query.filter(Patient.id.in_(patient_ids)).all()

    @staticmethod
    def create(patient: Patient) -> Patient:
        db.session.add(patient)
        db.session.commit()
        return patient

    @staticmethod
    def update(patient: Patient) -> Patient:
        db.session.commit()
        return patient

    @staticmethod
    def delete(patient: Patient) -> None:
        db.session.delete(patient)
        db.session.commit()

    @staticmethod
    def count() -> int:
        return Patient.query.count()

    @staticmethod
    def get_authorized_patient_ids_for_doctor(doctor_id: int) -> Set[int]:
        """Returns set of patient IDs assigned to or associated with doctor via appointments or records."""
        from app.models.appointment import Appointment
        from app.models.medical_record import MedicalRecord

        apt_ids = {a.patient_id for a in Appointment.query.filter_by(doctor_id=doctor_id).all()}
        mr_ids = {m.patient_id for m in MedicalRecord.query.filter_by(doctor_id=doctor_id).all()}
        return apt_ids.union(mr_ids)

    @staticmethod
    def get_patients_by_doctor(doctor_id: int) -> List[Patient]:
        """Returns list of patients assigned to or associated with doctor."""
        authorized_ids = PatientRepository.get_authorized_patient_ids_for_doctor(doctor_id)
        if not authorized_ids:
            return []
        return Patient.query.filter(Patient.id.in_(list(authorized_ids))).order_by(Patient.created_at.desc()).all()
