import uuid
from datetime import datetime
from app.extensions import db


class Appointment(db.Model):
    """Patient Appointment Scheduling Entity."""
    __tablename__ = 'appointments'

    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nurse_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(30), default=STATUS_SCHEDULED, nullable=False)
    reason = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Appointment ID: {self.id} PatientID: {self.patient_id} DoctorID: {self.doctor_id} Date: {self.appointment_date}>"
