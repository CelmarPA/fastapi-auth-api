import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.main import app
from app.database import Base, get_db
from app.models import User

SQL_URL = "sqlite:///./test.db"

engine_test = create_engine(SQL_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.drop_all(bind=engine_test)
Base.metadata.create_all(bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def create_user():
    def _create(email: str = "user@test.com", verified=True):
        db = TestingSessionLocal()

        user = User(
            email=email,
            hashed_password=hash_password("123456"),
            role="user",
            is_verified=verified,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()

        return user

    return _create


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
