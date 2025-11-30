def test_access_token_invalid(test_client):
    bad_token = "abc.def.ghi"
    response = test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401
