from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.auth_schema import (
    LoginSchema, RegisterSchema, RefreshTokenSchema,
    ForgotPasswordSchema, ResetPasswordSchema
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

login_schema = LoginSchema()
register_schema = RegisterSchema()
forgot_schema = ForgotPasswordSchema()
reset_schema = ResetPasswordSchema()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    errors = login_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    result = AuthService.authenticate_user(data['email'], data['password'])
    return jsonify({'status': 'success', 'data': result}), 200


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@roles_allowed(Role.ADMIN)
def register():
    data = request.get_json() or {}
    errors = register_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    user = AuthService.register_user(
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role_name=data['role_name']
    )
    return jsonify({
        'status': 'success',
        'message': 'User account created successfully.',
        'data': {
            'public_id': user.public_id,
            'email': user.email,
            'role': user.role.name
        }
    }), 201


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = int(get_jwt_identity())
    result = AuthService.refresh_access_token(user_id)
    return jsonify({'status': 'success', 'data': result}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    errors = forgot_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    token = AuthService.initiate_forgot_password(data['email'])
    return jsonify({
        'status': 'success',
        'message': 'Password reset request processed.',
        'reset_token': token
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    errors = reset_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    AuthService.reset_password(data['token'], data['new_password'])
    return jsonify({'status': 'success', 'message': 'Password has been reset successfully.'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    from app.repositories.user_repository import UserRepository
    user = UserRepository.get_by_id(user_id)
    return jsonify({
        'status': 'success',
        'data': {
            'public_id': user.public_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.name if user.role else None,
            'is_active': user.is_active
        }
    }), 200
