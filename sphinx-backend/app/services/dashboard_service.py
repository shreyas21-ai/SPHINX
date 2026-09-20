from typing import Dict, Any, Optional
from app.extensions import db
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.audit_repository import AuditRepository
from app.services.appointment_service import AppointmentService
from app.models.role import Role


class DashboardService:
    @staticmethod
    def get_dashboard_stats(user_id: Optional[int] = None, role_name: Optional[str] = None) -> Dict[str, Any]:
        """Gathers aggregated metric counts scoped to caller role."""
        if role_name == Role.DOCTOR and user_id:
            authorized_patient_ids = PatientRepository.get_authorized_patient_ids_for_doctor(user_id)
            today_appointments = AppointmentRepository.count_today_appointments_for_doctor(user_id)
            today_searches = AuditRepository.count_today_searches_for_user(user_id)
            upcoming_appointments = AppointmentService.get_doctor_appointments(user_id)

            return {
                'role': Role.DOCTOR,
                'statistics': {
                    'patient_count': len(authorized_patient_ids),
                    'today_appointments': today_appointments,
                    'today_searches': today_searches
                },
                'upcoming_appointments': upcoming_appointments[:5]
            }

        if role_name == Role.NURSE:
            nurse_appointments = AppointmentService.get_nurse_appointments(user_id) if user_id else []
            today_appointments = AppointmentRepository.count_today_appointments_for_nurse(user_id) if user_id else 0
            today_searches = AuditRepository.count_today_searches_for_user(user_id) if user_id else 0
            upcoming_count = len([a for a in nurse_appointments if a.get('status') == 'SCHEDULED'])
            unique_patients = len(set(a.get('patient_public_id') for a in nurse_appointments if a.get('patient_public_id')))

            return {
                'role': Role.NURSE,
                'statistics': {
                    'patient_count': unique_patients,
                    'today_appointments': today_appointments,
                    'upcoming_appointments_count': upcoming_count,
                    'today_searches': today_searches
                },
                'upcoming_appointments': nurse_appointments[:5]
            }

        if role_name == Role.INSURANCE_OFFICER:
            total_patients = PatientRepository.count()
            from app.models.billing import BillingRecord
            total_claims = BillingRecord.query.count()
            total_bill_amount = db.session.query(db.func.sum(BillingRecord.total_bill)).scalar() or 0.0
            approved_amount = db.session.query(db.func.sum(BillingRecord.approved_amount)).scalar() or 0.0
            patient_payable = db.session.query(db.func.sum(BillingRecord.patient_payable)).scalar() or 0.0

            return {
                'role': Role.INSURANCE_OFFICER,
                'statistics': {
                    'patient_count': total_patients,
                    'total_claims': total_claims,
                    'total_bill_amount': float(total_bill_amount),
                    'approved_amount': float(approved_amount),
                    'patient_payable': float(patient_payable)
                }
            }

        # Default / Admin Hospital-wide Stats
        total_patients = PatientRepository.count()
        total_doctors = UserRepository.count_doctors()
        today_appointments = AppointmentRepository.count_today_appointments()
        today_searches = AuditRepository.count_today_searches()
        audit_summary = AuditRepository.get_audit_summary()

        return {
            'role': role_name or Role.ADMIN,
            'statistics': {
                'patient_count': total_patients,
                'doctor_count': total_doctors,
                'today_appointments': today_appointments,
                'today_searches': today_searches
            },
            'audit_summary': audit_summary
        }
