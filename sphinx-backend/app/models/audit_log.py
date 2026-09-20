from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """
    Immutable Enterprise Audit Log Entity.
    Tracks access events, search operations, purpose declarations, and caller telemetry.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_role = db.Column(db.String(50), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True, index=True)
    purpose = db.Column(db.String(50), nullable=False, index=True)  # TREATMENT, BILLING, RESEARCH, EMERGENCY
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog User: {self.user_id} Role: {self.user_role} Action: {self.action} Purpose: {self.purpose}>"
