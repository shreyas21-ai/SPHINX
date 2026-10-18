from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.activity_monitor_service import ActivityMonitorService
from app.utils.rbac import roles_allowed
from app.models.role import Role

activity_bp = Blueprint('activity', __name__, url_prefix='/api/v1/dashboard')


@activity_bp.route('/alerts', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def get_alerts():
    """
    Returns active security alerts derived from audit and user data.
    Accessible only to ADMIN role.
    Alerts contain no patient medical content, passwords, or encryption keys.
    """
    result = ActivityMonitorService.get_all_alerts()
    return jsonify({
        'status': 'success',
        'data': result
    }), 200
