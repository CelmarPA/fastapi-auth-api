def test_logout(test_client, create_user):
    create_user()
    login = test_client.post("/auth/login", json={"email": "user@test.com", "password": "123456"})
    refresh = login.json()["refresh_token"]

    r = test_client.post("/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 200
