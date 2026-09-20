from datetime import datetime
from app.extensions import db


class Role(db.Model):
    """System Roles Model (Admin, Doctor, Nurse, Receptionist, Insurance Officer)."""
    __tablename__ = 'roles'

    ADMIN = 'ADMIN'
    DOCTOR = 'DOCTOR'
    NURSE = 'NURSE'
    RECEPTIONIST = 'RECEPTIONIST'
    INSURANCE_OFFICER = 'INSURANCE_OFFICER'

    ROLES_LIST = [ADMIN, DOCTOR, NURSE, RECEPTIONIST, INSURANCE_OFFICER]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f"<Role {self.name}>"
