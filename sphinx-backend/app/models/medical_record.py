import uuid
from datetime import datetime
from app.extensions import db


class MedicalRecord(db.Model):
    """
    Patient Medical Record Entity.
    All clinical fields are stored encrypted with AES-256-GCM.
    """
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # AES-256 Encrypted Clinical Fields
    disease_enc = db.Column(db.Text, nullable=True)
    diagnosis_enc = db.Column(db.Text, nullable=True)
    medical_history_enc = db.Column(db.Text, nullable=True)
    prescription_enc = db.Column(db.Text, nullable=True)
    lab_reports_enc = db.Column(db.Text, nullable=True)
    doctor_notes_enc = db.Column(db.Text, nullable=True)
    insurance_details_enc = db.Column(db.Text, nullable=True)
    treatment_plan_enc = db.Column(db.Text, nullable=True)
    allergies_enc = db.Column(db.Text, nullable=True)
    vitals_enc = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    search_indices = db.relationship('SearchIndex', backref='medical_record', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<MedicalRecord RecordID: {self.id} PatientID: {self.patient_id} DoctorID: {self.doctor_id}>"
