# app/tests/test_auth_refresh.py

"""
Refresh Token Tests
------------------

This module tests the refresh token functionality of the authentication API.

Test included:
- test_refresh_token: Ensure that a valid refresh token can be used to obtain new access and refresh tokens.
"""

from fastapi.testclient import TestClient


def test_refresh_token(test_client: TestClient, create_user):
    """
    Test successful refresh of tokens.

    Steps:
    1. Create a verified user.
    2. Login to get access and refresh tokens.
    3. Call the refresh endpoint with the refresh token.
    4. Assert that the response status code is 200.
    5. Assert that the response contains a new access token.

    :param test_client: TestClient fixture for API requests.
    :param create_user: Fixture to create a test user.
    """

    create_user()       # default verified=True
    login = test_client.post("/auth/login", json={"email": "user@test.com", "password": "123456"})
    refresh = login.json()["refresh_token"]

    response = test_client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    assert "access_token" in response.json()
