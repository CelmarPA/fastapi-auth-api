def test_login_success(test_client, create_user):
    create_user()
    payload = {"email": "user@test.com", "password": "123456"}

    response = test_client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_without_verification(test_client, create_user):
    create_user()
    payload = {"email": "user@ytest.com", "password": "123456"}

    r = test_client.post("/auth/login", json=payload)
    assert r.status_code == 401
