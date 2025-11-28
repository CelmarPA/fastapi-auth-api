from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def count(db: Session) -> int:
        return db.query(User).count()

    @staticmethod
    def create_user(db: Session, email: str, hashed_password: str, role: str) -> User:
        user = User(email=email, hashed_password=hashed_password, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_password(db: Session, user_id: int, hashed_password: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            user.hashed_password = hashed_password
            db.commit()

        return user

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 20):
        user_list = (
            db.query(User)
            .order_by(User.id.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return user_list

    @staticmethod
    def get(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update(db: Session, user: User, data: dict):

        if "email" in data:
            exists = db.query(User).filter(
                User.email == data["email"],
                User.id == user.id
            ).first()

            if exists:
                raise HTTPException(
                    status_code=400,
                    detail="Email already in use by another user"
                )

        for field, value in data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def disable(db: Session, user: User):
        user.is_active = False
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def enable(db: Session, user: User):
        user.is_active = True
        db.commit()
        db.refresh(user)

        return user

