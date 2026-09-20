from typing import List
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.utils.exceptions import NotFoundException, BadRequestException


class UserService:
    @staticmethod
    def get_user_by_public_id(public_id: str) -> User:
        user = UserRepository.get_by_public_id(public_id)
        if not user:
            raise NotFoundException("User not found.")
        return user

    @staticmethod
    def get_all_users() -> List[User]:
        return UserRepository.get_all()

    @staticmethod
    def update_user_status(public_id: str, is_active: bool) -> User:
        user = UserService.get_user_by_public_id(public_id)
        user.is_active = is_active
        return UserRepository.update(user)
