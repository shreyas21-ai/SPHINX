from typing import List, Dict, Any
from app.repositories.audit_repository import AuditRepository
from app.models.user import User


class AuditService:
    @staticmethod
    def list_logs(page: int = 1, per_page: int = 50) -> List[Dict[str, Any]]:
        logs = AuditRepository.get_logs(page=page, per_page=per_page)
        user_ids = {log.user_id for log in logs if log.user_id}
        users_map = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}

        res = []
        for log in logs:
            user = users_map.get(log.user_id) if log.user_id else None
            user_name = f"{user.first_name} {user.last_name}".strip() if user else (f"User #{log.user_id}" if log.user_id else "System")
            res.append({
                'id': log.id,
                'user_id': log.user_id,
                'user_name': user_name,
                'user_role': log.user_role,
                'action': log.action,
                'patient_id': log.patient_id,
                'purpose': log.purpose,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'timestamp': log.timestamp.isoformat()
            })
        return res

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        return AuditRepository.get_audit_summary()
