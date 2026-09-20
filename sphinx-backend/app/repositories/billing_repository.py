from typing import Optional, List
from app.extensions import db
from app.models.billing import BillingRecord


class BillingRepository:
    @staticmethod
    def create(billing_record: BillingRecord) -> BillingRecord:
        db.session.add(billing_record)
        db.session.commit()
        return billing_record

    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[BillingRecord]:
        return BillingRecord.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_patient_id(patient_id: int) -> List[BillingRecord]:
        return BillingRecord.query.filter_by(patient_id=patient_id).order_by(BillingRecord.created_at.desc()).all()
