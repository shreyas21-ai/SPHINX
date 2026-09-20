import uuid
from datetime import datetime
from app.extensions import db


class Patient(db.Model):
    """
    Patient Master Entity.
    Demographics and sensitive identities are stored in encrypted format (AES-256-GCM).
    """
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)

    # Encrypted PHI / PII Fields (AES-256-GCM ciphertexts)
    first_name_enc = db.Column(db.Text, nullable=False)
    last_name_enc = db.Column(db.Text, nullable=False)
    dob_enc = db.Column(db.Text, nullable=True)
    gender_enc = db.Column(db.Text, nullable=True)
    phone_enc = db.Column(db.Text, nullable=True)
    email_enc = db.Column(db.Text, nullable=True)
    address_enc = db.Column(db.Text, nullable=True)
    insurance_provider_enc = db.Column(db.Text, nullable=True)
    policy_number_enc = db.Column(db.Text, nullable=True)
    blood_group_enc = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    search_indices = db.relationship('SearchIndex', backref='patient', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Patient ID: {self.id} PublicID: {self.public_id}>"
