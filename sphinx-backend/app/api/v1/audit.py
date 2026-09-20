from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.audit_service import AuditService
from app.utils.rbac import roles_allowed
from app.models.role import Role

audit_bp = Blueprint('audit', __name__, url_prefix='/api/v1/audit')


@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    logs = AuditService.list_logs(page=page, per_page=per_page)
    return jsonify({
        'status': 'success',
        'total': len(logs),
        'data': logs
    }), 200


@audit_bp.route('/summary', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def get_audit_summary():
    summary = AuditService.get_summary()
    return jsonify({
        'status': 'success',
        'data': summary
    }), 200
