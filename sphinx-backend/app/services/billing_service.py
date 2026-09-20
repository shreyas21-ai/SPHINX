import json
from typing import Dict, Any, List
from app.models.billing import BillingRecord
from app.repositories.billing_repository import BillingRepository
from app.repositories.patient_repository import PatientRepository
from app.utils.exceptions import NotFoundException, BadRequestException


class BillingService:
    @staticmethod
    def create_billing_claim(data: Dict[str, Any], officer_id: int) -> Dict[str, Any]:
        patient_public_id = data.get('patient_public_id')
        patient = PatientRepository.get_by_public_id(patient_public_id)
        if not patient:
            raise NotFoundException("Patient record not found.")

        raw_items = data.get('items') or []
        if not raw_items:
            raise BadRequestException("At least one billing item is required.")

        calculated_items = []
        total_bill = 0.0

        for item in raw_items:
            name = item.get('item_name')
            qty = int(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0.0))
            amount = round(qty * unit_price, 2)
            total_bill += amount

            calculated_items.append({
                'item_name': name,
                'quantity': qty,
                'unit_price': unit_price,
                'amount': amount
            })

        total_bill = round(total_bill, 2)
        approved_amount = round(float(data.get('approved_amount', 0.0)), 2)
        patient_payable = round(max(0.0, total_bill - approved_amount), 2)

        record = BillingRecord(
            patient_id=patient.id,
            created_by_id=officer_id,
            items_json=json.dumps(calculated_items),
            total_bill=total_bill,
            approved_amount=approved_amount,
            patient_payable=patient_payable,
            insurance_provider=data.get('insurance_provider'),
            policy_number=data.get('policy_number'),
            claim_notes=data.get('claim_notes'),
            claim_status='APPROVED' if approved_amount > 0 else 'PROCESSED'
        )

        saved = BillingRepository.create(record)
        return BillingService.format_billing_record(saved, patient_public_id)

    @staticmethod
    def get_patient_billing_records(patient_public_id: str) -> List[Dict[str, Any]]:
        patient = PatientRepository.get_by_public_id(patient_public_id)
        if not patient:
            raise NotFoundException("Patient record not found.")

        records = BillingRepository.get_by_patient_id(patient.id)
        return [BillingService.format_billing_record(r, patient_public_id) for r in records]

    @staticmethod
    def get_billing_record_by_public_id(public_id: str) -> Dict[str, Any]:
        record = BillingRepository.get_by_public_id(public_id)
        if not record:
            raise NotFoundException("Billing statement record not found.")

        patient_public_id = record.patient.public_id if record.patient else ''
        return BillingService.format_billing_record(record, patient_public_id)

    @staticmethod
    def format_billing_record(record: BillingRecord, patient_public_id: str) -> Dict[str, Any]:
        try:
            items = json.loads(record.items_json)
        except Exception:
            items = []

        return {
            'public_id': record.public_id,
            'patient_public_id': patient_public_id,
            'items': items,
            'total_bill': record.total_bill,
            'approved_amount': record.approved_amount,
            'patient_payable': record.patient_payable,
            'insurance_provider': record.insurance_provider,
            'policy_number': record.policy_number,
            'claim_status': record.claim_status,
            'claim_notes': record.claim_notes,
            'created_at': record.created_at.isoformat() if record.created_at else None
        }
