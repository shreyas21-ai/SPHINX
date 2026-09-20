from typing import Optional, List
from datetime import datetime, date
from app.extensions import db
from app.models.appointment import Appointment


class AppointmentRepository:
    @staticmethod
    def get_by_id(appointment_id: int) -> Optional[Appointment]:
        return Appointment.query.get(appointment_id)

    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[Appointment]:
        return Appointment.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_patient_id(patient_id: int) -> List[Appointment]:
        return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()

    @staticmethod
    def get_by_doctor_id(doctor_id: int) -> List[Appointment]:
        return Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.appointment_date.desc()).all()

    @staticmethod
    def get_by_nurse_id(nurse_id: int) -> List[Appointment]:
        return Appointment.query.filter_by(nurse_id=nurse_id).order_by(Appointment.appointment_date.desc()).all()

    @staticmethod
    def create(appointment: Appointment) -> Appointment:
        db.session.add(appointment)
        db.session.commit()
        return appointment

    @staticmethod
    def update(appointment: Appointment) -> Appointment:
        db.session.commit()
        return appointment

    @staticmethod
    def delete(appointment: Appointment) -> None:
        db.session.delete(appointment)
        db.session.commit()

    @staticmethod
    def count_today_appointments() -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        return Appointment.query.filter(Appointment.appointment_date >= today_start, Appointment.appointment_date <= today_end).count()

    @staticmethod
    def count_today_appointments_for_doctor(doctor_id: int) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        return Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date <= today_end
        ).count()

    @staticmethod
    def count_today_appointments_for_nurse(nurse_id: int) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        return Appointment.query.filter(
            Appointment.nurse_id == nurse_id,
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date <= today_end
        ).count()
