from app.api.v1.auth import auth_bp
from app.api.v1.users import users_bp
from app.api.v1.patients import patients_bp
from app.api.v1.medical_records import medical_records_bp
from app.api.v1.appointments import appointments_bp
from app.api.v1.search import search_bp
from app.api.v1.dashboard import dashboard_bp
from app.api.v1.audit import audit_bp
from app.api.v1.billing import billing_bp
from app.api.v1.activity import activity_bp

v1_blueprints = [
    auth_bp, users_bp, patients_bp, medical_records_bp,
    appointments_bp, search_bp, dashboard_bp, audit_bp, billing_bp,
    activity_bp
]

__all__ = ['v1_blueprints']

