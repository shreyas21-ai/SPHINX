from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils.exceptions import PurposeRequiredException

from app.models.role import Role

VALID_PURPOSES = {'TREATMENT', 'BILLING', 'RESEARCH', 'EMERGENCY', 'ADMINISTRATIVE', 'APPOINTMENT'}

ROLE_PURPOSES_MAP = {
    Role.ADMIN: {'ADMINISTRATIVE'},
    Role.DOCTOR: {'TREATMENT', 'EMERGENCY', 'RESEARCH'},
    Role.NURSE: {'TREATMENT', 'EMERGENCY'},
    Role.RECEPTIONIST: {'ADMINISTRATIVE', 'APPOINTMENT'},
    Role.INSURANCE_OFFICER: {'BILLING'}
}


def audit_log(action: str, require_purpose: bool = True):
    """
    Decorator that enforces access purpose validation and logs access telemetry to AuditLogs table.
    Captures: Who (user_id/role), When (timestamp), Why (purpose), Patient (patient_id), Action, IP, User Agent.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            user_role = user.role.name if user and user.role else 'UNKNOWN'

            # Extract purpose from header X-Access-Purpose or request query/json
            purpose = request.headers.get('X-Access-Purpose')
            if not purpose and request.is_json and request.json:
                purpose = request.json.get('purpose')
            if not purpose:
                purpose = request.args.get('purpose')

            if require_purpose:
                if not purpose or purpose.upper() not in VALID_PURPOSES:
                    raise PurposeRequiredException("Explicit valid access purpose declaration is required.")

                purpose = purpose.upper()
                allowed_role_purposes = ROLE_PURPOSES_MAP.get(user_role, set())
                if purpose not in allowed_role_purposes:
                    raise PurposeRequiredException(
                        f"Access purpose '{purpose}' is not authorized for role '{user_role}'. Allowed: {list(allowed_role_purposes)}"
                    )
            else:
                purpose = (purpose.upper() if purpose else 'GENERAL')

            # Extract patient_id if present in kwargs or request
            patient_id = kwargs.get('patient_id') or kwargs.get('id')
            if not patient_id and request.is_json and request.json:
                patient_id = request.json.get('patient_id')

            # Log to DB
            log_entry = AuditLog(
                user_id=user_id,
                user_role=user_role,
                action=action,
                patient_id=int(patient_id) if patient_id and str(patient_id).isdigit() else None,
                purpose=purpose,
                ip_address=request.remote_addr or request.headers.get('X-Forwarded-For', '127.0.0.1'),
                user_agent=request.user_agent.string[:250] if request.user_agent else 'Unknown'
            )
            try:
                db.session.add(log_entry)
                db.session.commit()
            except Exception:
                db.session.rollback()

            return fn(*args, **kwargs)
        return wrapper
    return decorator
