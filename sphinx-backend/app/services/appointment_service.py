from typing import Dict, Any, List, Optional
from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import NotFoundException, BadRequestException


class AppointmentService:
    @staticmethod
    def create_appointment(appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.models.role import Role
        patient_public_id = appointment_data.get('patient_public_id')
        doctor_public_id = appointment_data.get('doctor_public_id')
        nurse_public_id = appointment_data.get('nurse_public_id')

        patient = PatientRepository.get_by_public_id(patient_public_id)
        if not patient:
            raise NotFoundException("Patient not found.")

        doctor = UserRepository.get_by_public_id(doctor_public_id)
        if not doctor or not doctor.is_active or (doctor.role and doctor.role.name != Role.DOCTOR):
            raise BadRequestException("Invalid or inactive Doctor selected.")

        nurse = None
        if nurse_public_id:
            nurse = UserRepository.get_by_public_id(nurse_public_id)
            if not nurse or not nurse.is_active or (nurse.role and nurse.role.name != Role.NURSE):
                raise BadRequestException("Invalid or inactive Nurse selected.")

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            nurse_id=nurse.id if nurse else None,
            appointment_date=appointment_data.get('appointment_date'),
            reason=appointment_data.get('reason'),
            status=Appointment.STATUS_SCHEDULED
        )
        saved = AppointmentRepository.create(appointment)
        return AppointmentService.format_appointment(saved)

    @staticmethod
    def format_appointment(appointment: Appointment) -> Dict[str, Any]:
        patient = PatientRepository.get_by_id(appointment.patient_id)
        doctor = UserRepository.get_by_id(appointment.doctor_id)
        nurse = UserRepository.get_by_id(appointment.nurse_id) if appointment.nurse_id else None

        from app.crypto.aes_cipher import AESCipher
        first = AESCipher.decrypt(patient.first_name_enc) if (patient and patient.first_name_enc) else ''
        last = AESCipher.decrypt(patient.last_name_enc) if (patient and patient.last_name_enc) else ''
        patient_name = f"{first} {last}".strip() if (first or last) else 'Patient'

        return {
            'public_id': appointment.public_id,
            'patient_public_id': patient.public_id if patient else None,
            'patient_name': patient_name,
            'doctor_public_id': doctor.public_id if doctor else None,
            'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else None,
            'nurse_public_id': nurse.public_id if nurse else None,
            'nurse_name': f"{nurse.first_name} {nurse.last_name}" if nurse else 'Unassigned',
            'appointment_date': appointment.appointment_date.isoformat(),
            'status': appointment.status,
            'reason': appointment.reason,
            'created_at': appointment.created_at.isoformat()
        }

    @staticmethod
    def get_appointment_by_public_id(public_id: str) -> Dict[str, Any]:
        apt = AppointmentRepository.get_by_public_id(public_id)
        if not apt:
            raise NotFoundException("Appointment not found.")
        return AppointmentService.format_appointment(apt)

    @staticmethod
    def update_status(public_id: str, new_status: str) -> Dict[str, Any]:
        apt = AppointmentRepository.get_by_public_id(public_id)
        if not apt:
            raise NotFoundException("Appointment not found.")

        if new_status not in [Appointment.STATUS_SCHEDULED, Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED]:
            raise BadRequestException("Invalid appointment status.")

        apt.status = new_status
        updated = AppointmentRepository.update(apt)
        return AppointmentService.format_appointment(updated)

    @staticmethod
    def get_doctor_appointments(doctor_id: int) -> List[Dict[str, Any]]:
        apts = AppointmentRepository.get_by_doctor_id(doctor_id)
        return [AppointmentService.format_appointment(a) for a in apts]

    @staticmethod
    def get_nurse_appointments(nurse_id: int) -> List[Dict[str, Any]]:
        apts = AppointmentRepository.get_by_nurse_id(nurse_id)
        return [AppointmentService.format_appointment(a) for a in apts]

    @staticmethod
    def list_appointments(role_name: str, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        from app.models.role import Role
        if role_name == Role.DOCTOR and user_id:
            apts = AppointmentRepository.get_by_doctor_id(user_id)
        elif role_name == Role.NURSE and user_id:
            apts = AppointmentRepository.get_by_nurse_id(user_id)
        else:
            apts = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
        return [AppointmentService.format_appointment(a) for a in apts]
