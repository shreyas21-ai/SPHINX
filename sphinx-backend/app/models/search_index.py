from datetime import datetime
from app.extensions import db


class SearchIndex(db.Model):
    """
    HMAC-based Cryptographic Blind Search Index.
    Stores irreversible HMAC token hashes mapped to Patient and Medical Record IDs.
    Enables sub-second exact and substring queries without full-database decryption.
    """
    __tablename__ = 'search_index'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=True, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='CASCADE'), nullable=True, index=True)
    field_name = db.Column(db.String(50), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA-256 hex string is 64 chars
    token_type = db.Column(db.String(20), nullable=False, default='EXACT')  # 'EXACT' or 'NGRAM'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_token_field_record', 'token_hash', 'field_name', 'record_id'),
        db.Index('idx_token_field_patient', 'token_hash', 'field_name', 'patient_id'),
    )

    def __repr__(self):
        return f"<SearchIndex Field: {self.field_name} Type: {self.token_type} Hash: {self.token_hash[:10]}...>"
