from typing import List, Dict, Any
from datetime import datetime, date
from sqlalchemy import func
from app.extensions import db
from app.models.audit_log import AuditLog


class AuditRepository:
    @staticmethod
    def get_logs(page: int = 1, per_page: int = 50) -> List[AuditLog]:
        return AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False).items

    @staticmethod
    def get_logs_by_user(user_id: int) -> List[AuditLog]:
        return AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.timestamp.desc()).all()

    @staticmethod
    def get_logs_by_patient(patient_id: int) -> List[AuditLog]:
        return AuditLog.query.filter_by(patient_id=patient_id).order_by(AuditLog.timestamp.desc()).all()

    @staticmethod
    def count_today_searches() -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        return AuditLog.query.filter(
            AuditLog.action.like('%SEARCH%'),
            AuditLog.timestamp >= today_start,
            AuditLog.timestamp <= today_end
        ).count()

    @staticmethod
    def count_today_searches_for_user(user_id: int) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        return AuditLog.query.filter(
            AuditLog.user_id == user_id,
            AuditLog.action.like('%SEARCH%'),
            AuditLog.timestamp >= today_start,
            AuditLog.timestamp <= today_end
        ).count()

    @staticmethod
    def get_audit_summary() -> Dict[str, Any]:
        total_logs = AuditLog.query.count()
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_logs = AuditLog.query.filter(AuditLog.timestamp >= today_start).count()

        purpose_counts = db.session.query(
            AuditLog.purpose, func.count(AuditLog.id)
        ).group_by(AuditLog.purpose).all()

        role_counts = db.session.query(
            AuditLog.user_role, func.count(AuditLog.id)
        ).group_by(AuditLog.user_role).all()

        return {
            'total_audit_events': total_logs,
            'today_audit_events': today_logs,
            'events_by_purpose': dict(purpose_counts),
            'events_by_role': dict(role_counts)
        }
