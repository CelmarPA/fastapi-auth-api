# app/tests/conftest.py

"""
Pytest Fixtures and Test Configuration
--------------------------------------

This module sets up the testing environment for FastAPI with SQLAlchemy.

Fixtures provided:
- test_client: Returns a TestClient instance for API calls.
- create_user: Helper fixture to create a user in the test database.
- clean_db: Automatically cleans and recreates database tables before each test.
"""
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.main import app
from app.database import Base, get_db
from app.models import User


# ---------------------------
# TEST DATABASE CONFIG
# ---------------------------
SQL_URL = "sqlite:///./test.db"

engine_test = create_engine(SQL_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Drop all tables and recreate for clean state
Base.metadata.drop_all(bind=engine_test)
Base.metadata.create_all(bind=engine_test)


# ---------------------------
# OVERRIDE DEPENDENCIES
# ---------------------------
def override_get_db():
    """
    Override the get_db dependency to use the test database session.

    :yield: SQLAlchemy Session connected to the test database.
    :rtype: Session
    """

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------
# FIXTURES
# ---------------------------
@pytest.fixture
def test_client() -> TestClient:
    """
    Provides a FastAPI TestClient for making API requests in tests.

    :return: TestClient instance for the FastAPI app.
    :rtype: TestClient
    """

    return TestClient(app)


@pytest.fixture
def create_user() -> Callable:
    """
    Factory fixture to create a user in the test database.

    :return: Function that creates a user with specified email and verification status.
    :rtype: callable
    """

    def _create(email: str = "user@test.com", verified=True) -> User:
        """
        Create a single user record.

        :param email: Email of the user to create.
        :type email: str

        :param verified: Whether the user should be marked as verified.
        :type verified: bool

        :return: Created User instance.
        :rtype: User
        """

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
    """
    Automatically drops and recreates all database tables before each test.

    Ensures tests run in a clean database state.
    """

    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
