def test_register_user(test_client):
    payload = {"email": "new@test.com", "password": "123456"}
    response = test_client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert "id" in data
