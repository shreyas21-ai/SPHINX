import uuid
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.utils.exceptions import BadRequestException, UnauthorizedException, NotFoundException


class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        from app.extensions import db
        user = UserRepository.get_by_email(email)

        # Track failed attempts before raising — always look up by email
        if not user or not user.check_password(password):
            if user:
                # Increment failed counter and persist safely
                try:
                    user.failed_login_count = (user.failed_login_count or 0) + 1
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled.")

        # Successful login: reset failure counter and record timestamp
        try:
            user.failed_login_count = 0
            user.last_login_at = datetime.utcnow()
            db.session.commit()
        except Exception:
            db.session.rollback()

        identity = str(user.id)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'public_id': user.public_id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.name if user.role else None
            }
        }

    @staticmethod
    def register_user(email: str, password: str, first_name: str, last_name: str, role_name: str) -> User:
        existing = UserRepository.get_by_email(email)
        if existing:
            raise BadRequestException("User with this email already exists.")

        role = UserRepository.get_role_by_name(role_name)
        if not role:
            raise BadRequestException(f"Role '{role_name}' does not exist.")

        user = User(
            email=email.lower().strip(),
            first_name=first_name,
            last_name=last_name,
            role_id=role.id
        )
        user.set_password(password)
        return UserRepository.create(user)

    @staticmethod
    def refresh_access_token(user_id: int) -> dict:
        user = UserRepository.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Invalid user context for token refresh.")

        new_access_token = create_access_token(identity=str(user.id))
        return {'access_token': new_access_token}

    @staticmethod
    def initiate_forgot_password(email: str) -> str:
        user = UserRepository.get_by_email(email)
        if not user:
            # For security, return token placeholder without throwing exception
            return "If an account exists, a reset token has been generated."

        token = str(uuid.uuid4())
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        UserRepository.update(user)
        return token

    @staticmethod
    def reset_password(token: str, new_password: str) -> None:
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            raise BadRequestException("Invalid or expired password reset token.")

        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        UserRepository.update(user)
