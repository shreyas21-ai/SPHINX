from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.dashboard_service import DashboardService
from app.repositories.user_repository import UserRepository
from app.utils.rbac import roles_allowed
from app.models.role import Role

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST, Role.INSURANCE_OFFICER)
def get_dashboard_stats():
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'RECEPTIONIST'

    stats = DashboardService.get_dashboard_stats(user_id=user_id, role_name=role_name)
    return jsonify({
        'status': 'success',
        'data': stats
    }), 200
