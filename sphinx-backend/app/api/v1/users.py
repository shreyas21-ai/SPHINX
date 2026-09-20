from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.utils.rbac import roles_allowed
from app.models.role import Role

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def list_users():
    users = UserService.get_all_users()
    data = [{
        'public_id': u.public_id,
        'email': u.email,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'role': u.role.name if u.role else None,
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat()
    } for u in users]
    return jsonify({'status': 'success', 'data': data}), 200


@users_bp.route('/<public_id>', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def get_user(public_id):
    u = UserService.get_user_by_public_id(public_id)
    return jsonify({
        'status': 'success',
        'data': {
            'public_id': u.public_id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': u.role.name if u.role else None,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat()
        }
    }), 200


@users_bp.route('/<public_id>/status', methods=['PATCH'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def update_status(public_id):
    req = request.get_json() or {}
    is_active = req.get('is_active', True)
    u = UserService.update_user_status(public_id, is_active)
    return jsonify({
        'status': 'success',
        'message': f"User status updated to {'active' if is_active else 'inactive'}.",
        'data': {'public_id': u.public_id, 'is_active': u.is_active}
    }), 200


@users_bp.route('/doctors', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST, Role.NURSE)
def list_doctors():
    from app.repositories.user_repository import UserRepository
    doctors = UserRepository.get_doctors()
    data = [{
        'public_id': u.public_id,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'email': u.email
    } for u in doctors]
    return jsonify({'status': 'success', 'data': data}), 200


@users_bp.route('/nurses', methods=['GET'])
@jwt_required()
@roles_allowed(Role.ADMIN, Role.DOCTOR, Role.RECEPTIONIST, Role.NURSE)
def list_nurses():
    from app.repositories.user_repository import UserRepository
    nurses = UserRepository.get_nurses()
    data = [{
        'public_id': u.public_id,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'email': u.email
    } for u in nurses]
    return jsonify({'status': 'success', 'data': data}), 200
