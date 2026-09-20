from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app.utils.exceptions import ForbiddenException, UnauthorizedException


def roles_allowed(*allowed_roles):
    """
    Decorator enforcing that the authenticated JWT user belongs to at least one of the specified allowed roles.
    Usage: @roles_allowed('ADMIN', 'DOCTOR')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_active:
                raise UnauthorizedException("User account is inactive or invalid.")

            user_role_name = user.role.name if user.role else None

            if user_role_name not in allowed_roles:
                raise ForbiddenException(
                    f"Role '{user_role_name}' is not authorized to access this resource. Allowed: {list(allowed_roles)}"
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def role_required(role_name: str):
    """
    Decorator requiring a single specific role.
    Usage: @role_required('ADMIN')
    """
    return roles_allowed(role_name)
