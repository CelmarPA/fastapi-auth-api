def test_refresh_token(test_client, create_user):
    create_user()
    login = test_client.post("/auth/login", json={"email": "user@test.com", "password": "123456"})
    refresh = login.json()["refresh_token"]

    response = test_client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    assert "access_token" in response.json()
