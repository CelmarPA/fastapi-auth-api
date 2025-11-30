def test_admin_rout_forbidden(test_client, create_user):
    create_user("user@test.com")
    login = test_client.post("/auth/login", json={"email": "user@test.com", "password": "123456"})

    token = login.json()["access_token"]

    response = test_client.get(
        "/admin/users/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    