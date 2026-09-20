from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.search_schema import SearchQuerySchema
from app.services.search_service import SearchService
from app.repositories.user_repository import UserRepository
from app.utils.rbac import roles_allowed
from app.utils.audit_decorator import audit_log
from app.models.role import Role

search_bp = Blueprint('search', __name__, url_prefix='/api/v1/search')
search_schema = SearchQuerySchema()


@search_bp.route('', methods=['POST'])
@jwt_required()
@roles_allowed(Role.DOCTOR, Role.NURSE)
@audit_log(action='SEARCHABLE_ENCRYPTION_QUERY', require_purpose=True)
def execute_search():
    """
    Executes blind HMAC searchable encryption lookup across encrypted database.
    Does NOT decrypt non-matching database entries.
    Requires purpose header X-Access-Purpose or json field.
    """
    user_id = int(get_jwt_identity())
    user = UserRepository.get_by_id(user_id)
    role_name = user.role.name if user and user.role else 'RECEPTIONIST'

    data = request.get_json() or {}
    errors = search_schema.validate(data)
    if errors:
        return jsonify({'status': 'error', 'errors': errors}), 400

    results = SearchService.search_records(data, role_name=role_name, user_id=user_id)
    return jsonify({
        'status': 'success',
        'data': results
    }), 200
