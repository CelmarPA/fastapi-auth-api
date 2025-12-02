# app/tests/conftest.py

"""
Pytest Fixtures and Test Configuration
--------------------------------------

This module sets up the testing environment for FastAPI with SQLAlchemy and provides
reusable fixtures for unit and integration tests.

Fixtures included:

- `test_client`: Returns a TestClient instance for API requests.
- `create_user`: Factory to create users in the test database.
- `create_admin_user`: Factory to create admin users.
- `create_product_in_db`: Factory to create product records.
- `mock_email_client`: Automatically mocks email sending to prevent real emails.
- `clean_db`: Automatically resets the database tables before each test.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Callable

from app.core.security import hash_password
from app.services.email_client import EmailClient
from app.main import app
from app.database import Base, get_db
from app.models import User, Product


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
def override_get_db() -> Session:
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
def db_session() -> Session:
    """
    Provides a fresh SQLAlchemy session for tests.

    :return: SQLAlchemy Session instance.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    :rtype: Callable
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
def mock_email_client(monkeypatch)-> Callable:
    """
    Automatically mocks the EmailClient.send_email method to prevent real emails
    from being sent during tests.

    The mock prints the email details for debugging purposes.
    """

    def fake_send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Fake email sender that prints the email info instead of sending.

        :param to_email: Recipient email address.
        :type to_email: str

        :param subject: Email subject line.
        :type subject: str

        :param html_content: HTML content of the email.
        :type html_content: str

        :return: Always returns True to simulate successful sending.
        :rtype: bool
        """
        _html_content = html_content

        print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        return True

    monkeypatch.setattr(EmailClient, "send_email", fake_send_email)


@pytest.fixture
def create_admin_user() -> Callable:
    """
    Factory fixture to create an admin user in the test database.

    :return: Callable function that creates an admin user.
    :rtype: Callable
    """

    def _create(email="admin@test.com") -> User:
        """
        Creates a single admin user record in the test database.

        :param email: Email of the admin user to create.
        :type email: str

        :return: Created admin User instance.
        :rtype: User
        """

        db = TestingSessionLocal()

        user = User(
            email=email,
            hashed_password=hash_password("123456"),
            role="admin",
            is_verified=True,
            is_active=True

        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()

        return user

    return _create


@pytest.fixture
def create_product_in_db() -> Callable:
    """
    Factory fixture to create product records in the test database.

    Allows optional customization of product fields.

    :return: Callable function that creates a product.
    :rtype: Callable
    """

    def _create(
        name: str = "Default Product",
        description: str = "Default description",
        price: float = 10.0,
        stock: int = 5,
        db: Session = None
    ) -> Product:
        """
        Creates a product record in the database.

        :param name: Name of the product.
        :type name: str

        :param description: Product description.
        :type description: str

        :param price: Price of the product.
        :type price: float

        :param stock: Stock quantity of the product.
        :type stock: int

        :param db: Optional SQLAlchemy Session. Uses TestingSessionLocal if None.
        :type db: Session, optional

        :return: Created Product instance.
        :rtype: Product
        """

        if db is None:
            db = TestingSessionLocal()

        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    return _create



@pytest.fixture(autouse=True)
def clean_db() -> None:
    """
    Automatically drops and recreates all database tables before each test.

    Ensures each test starts with a clean database state to prevent
    test data contamination.

    :return: None
    """

    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
