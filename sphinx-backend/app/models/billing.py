from datetime import datetime
import uuid
from app.extensions import db


class BillingRecord(db.Model):
    """Hospital Billing and Insurance Claim Model."""
    __tablename__ = 'billing_records'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # JSON representation of itemized charges: [{item_name, quantity, unit_price, amount}]
    items_json = db.Column(db.Text, nullable=False)

    # Billing calculations
    total_bill = db.Column(db.Float, nullable=False, default=0.0)
    approved_amount = db.Column(db.Float, nullable=False, default=0.0)
    patient_payable = db.Column(db.Float, nullable=False, default=0.0)

    # Contextual info for insurance claim
    insurance_provider = db.Column(db.String(100), nullable=True)
    policy_number = db.Column(db.String(100), nullable=True)
    claim_status = db.Column(db.String(50), default='PROCESSED')
    claim_notes = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('billing_records', lazy=True))
    created_by = db.relationship('User', backref=db.backref('created_billing_records', lazy=True))

    def __repr__(self):
        return f"<BillingRecord #{self.public_id} Total={self.total_bill} Payable={self.patient_payable}>"
