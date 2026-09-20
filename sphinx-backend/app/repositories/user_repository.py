from typing import Optional, List
from app.extensions import db
from app.models.user import User
from app.models.role import Role


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[User]:
        return User.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email.lower().strip()).first()

    @staticmethod
    def get_all() -> List[User]:
        return User.query.all()

    @staticmethod
    def get_role_by_name(role_name: str) -> Optional[Role]:
        return Role.query.filter_by(name=role_name.upper()).first()

    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[Role]:
        return Role.query.get(role_id)

    @staticmethod
    def create(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User) -> User:
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def count_doctors() -> int:
        doctor_role = Role.query.filter_by(name=Role.DOCTOR).first()
        if not doctor_role:
            return 0
        return User.query.filter_by(role_id=doctor_role.id, is_active=True).count()

    @staticmethod
    def get_doctors() -> List[User]:
        doctor_role = Role.query.filter_by(name=Role.DOCTOR).first()
        if not doctor_role:
            return []
        return User.query.filter_by(role_id=doctor_role.id, is_active=True).all()

    @staticmethod
    def get_nurses() -> List[User]:
        nurse_role = Role.query.filter_by(name=Role.NURSE).first()
        if not nurse_role:
            return []
        return User.query.filter_by(role_id=nurse_role.id, is_active=True).all()
