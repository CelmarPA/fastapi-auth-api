# app/tests/test_auth_login.py

"""
Authentication Tests
--------------------

This module contains tests for the authentication endpoints of the API.

Tests included:
- test_login_success: Ensure a verified user can log in successfully.
- test_login_without_verification: Ensure unverified users cannot log in.
"""

from fastapi.testclient import TestClient


def test_login_success(test_client: TestClient, create_user):
    """
    Test successful login for a verified user.

    Steps:
    1. Create a verified user using the create_user fixture.
    2. Attempt login with correct credentials.
    3. Assert that status code is 200 and response contains an access token.

    :param test_client: TestClient fixture for API requests.
    :param create_user: Fixture to create a test user.
    """

    create_user()
    payload = {"email": "user@test.com", "password": "123456"}

    response = test_client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_without_verification(test_client: TestClient, create_user):
    """
    Test login attempt for a user whose email is not verified.

    Steps:
    1. Create an unverified user.
    2. Attempt login with correct credentials.
    3. Assert that status code is 401 (unauthorized).

    :param test_client: TestClient fixture for API requests.
    :param create_user: Fixture to create a test user.
    """

    create_user()
    payload = {"email": "user@ytest.com", "password": "123456"}

    r = test_client.post("/auth/login", json=payload)
    assert r.status_code == 401
