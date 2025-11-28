from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password


class UserService:

    @staticmethod
    def list_users(db: Session, page: int, limit: int):
        skip = (page - 1) * limit
        users = UserRepository.list(db, skip, limit)

        return users

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = UserRepository.get(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data: dict):
        user = UserRepository.get(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserRepository.update(db, user, data)

    @staticmethod
    def disable_user(db: Session, user_id: int):
        user = UserRepository.get(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserRepository.disable(db, user)

    @staticmethod
    def enable_user(db: Session, user_id: int):
        user = UserRepository.get(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserRepository.enable(db, user)
