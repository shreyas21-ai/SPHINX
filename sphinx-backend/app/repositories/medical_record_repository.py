from typing import Optional, List
from app.extensions import db
from app.models.medical_record import MedicalRecord


class MedicalRecordRepository:
    @staticmethod
    def get_by_id(record_id: int) -> Optional[MedicalRecord]:
        return MedicalRecord.query.get(record_id)

    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[MedicalRecord]:
        return MedicalRecord.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_patient_id(patient_id: int) -> List[MedicalRecord]:
        return MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()

    @staticmethod
    def get_by_ids(record_ids: List[int]) -> List[MedicalRecord]:
        if not record_ids:
            return []
        return MedicalRecord.query.filter(MedicalRecord.id.in_(record_ids)).all()

    @staticmethod
    def get_by_patient_ids(patient_ids: List[int]) -> List[MedicalRecord]:
        if not patient_ids:
            return []
        return MedicalRecord.query.filter(MedicalRecord.patient_id.in_(patient_ids)).all()

    @staticmethod
    def create(record: MedicalRecord) -> MedicalRecord:
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def update(record: MedicalRecord) -> MedicalRecord:
        db.session.commit()
        return record

    @staticmethod
    def delete(record: MedicalRecord) -> None:
        db.session.delete(record)
        db.session.commit()
