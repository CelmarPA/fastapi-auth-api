# app/tests/test_auth_logout.py

"""
Logout Tests
------------

This module tests the logout endpoint of the authentication API.

Test included:
- test_logout: Ensure that a logged-in user can successfully log out by revoking the refresh token.
"""

from fastapi.testclient import TestClient


def test_logout(test_client: TestClient, create_user):
    """
    Test successful logout of a user.

    Steps:
    1. Create a verified user.
    2. Login to get access and refresh tokens.
    3. Call the logout endpoint with the refresh token.
    4. Assert that the response status code is 200.

    :param test_client: TestClient fixture for API requests.
    :param create_user: Fixture to create a test user.
    """

    create_user()   # default verified=True
    login = test_client.post("/auth/login", json={"email": "user@test.com", "password": "123456"})
    refresh = login.json()["refresh_token"]

    r = test_client.post("/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 200
