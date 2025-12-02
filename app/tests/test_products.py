# app/tests/test_products.py


"""
Products API Tests
------------------

This module tests all CRUD operations for the products API, including:

1. Listing products
2. Creating products (authorized and unauthorized)
3. Updating products
4. Deleting products
5. Handling non-existent products

All tests use the FastAPI TestClient and database fixtures.
"""

from fastapi.testclient import TestClient
from typing import Callable

from app.tests.conftest import create_admin_user


def test_list_products(test_client: TestClient, create_product_in_db: Callable) -> None:
    """
    Test retrieving a list of products.

    Steps:
    1. Create two products in the test database.
    2. Call the /products/ endpoint.
    3. Assert the response status code and that at least 2 products are returned.

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_product_in_db: Factory function to create a product in the database.
    :type create_product_in_db: Callable

    :return: None
    """

    create_product_in_db(name="Prod 1", description="Desc 1", price=20.0, stock=5)
    create_product_in_db(name="Prod 2", description="Desc 2", price=30.0, stock=5)

    response = test_client.get("/products/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2


def test_create_product_authorized(test_client: TestClient, create_admin_user: Callable) -> None:
    """
    Test that an admin user can create a product.

    Steps:
    1. Create an admin user and log in to get a token.
    2. Send a POST request to /products/ with product data.
    3. Assert the response status code and returned product data.

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_admin_user: Factory function to create an admin user.
    :type create_admin_user: Callable

    :return: None
    """

    user = create_admin_user()

    # Login to get token
    login = test_client.post("/auth/login", json={"email": user.email, "password": "123456"})
    token = login.json()["access_token"]

    payload = {
        "name": "New Product",
        "description": "New Product Description",
        "price": 20.0,
        "stock": 10
    }

    response = test_client.post("/products/", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "New Product"


def test_create_product_unauthorized(test_client: TestClient, create_user: Callable) -> None:
    """
    Test that a non-admin user cannot create a product.

    Steps:
    1. Create a regular user and log in to get a token.
    2. Attempt to POST a new product with this user's token.
    3. Assert that the response status code is 403 (Forbidden).

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_user: Factory function to create a regular user.
    :type create_user: Callable

    :return: None
    """

    user = create_user(email="user@test.com", verified=True)
    login_resp = test_client.post("/auth/login", json={"email": user.email, "password": "123456"})
    token = login_resp.json()["access_token"]

    payload = {
        "name": "Hacker Product",
        "description": "Hacker Product Description",
        "price": 99.9,
        "stock": 1
    }

    response = test_client.post(
        "/products/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403  # sem token/admin


def test_update_product(test_client: TestClient, create_admin_user: Callable, create_product_in_db: Callable) -> None:
    """
    Test updating an existing product by an admin user.

    Steps:
    1. Create an admin user and log in.
    2. Create a product in the database.
    3. Send a PUT request to update the product.
    4. Assert the response status code and updated fields.

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_admin_user: Factory to create an admin user.
    :type create_admin_user: Callable

    :param create_product_in_db: Factory to create a product in the database.
    :type create_product_in_db: Callable

    :return: None
    """

    user = create_admin_user(email="admin@test.com")

    login = test_client.post("/auth/login", json={"email": user.email, "password": "123456"})
    token = login.json()["access_token"]

    product = create_product_in_db(name="Old Product", description="Old desc", price=5.0, stock=2)

    data = {"name": "Updated Product", "description": "Updated desc", "price": 15.0, "stock": 10}

    response = test_client.put(
        f"/products/{product.id}",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    resp_data = response.json()

    assert resp_data["name"] == data["name"]
    assert resp_data["description"] == data["description"]
    assert resp_data["price"] == data["price"]
    assert resp_data["stock"] == data["stock"]


def test_delete_product(test_client: TestClient, create_admin_user: Callable, create_product_in_db: Callable) -> None:
    """
    Test deleting a product by an admin user.

    Steps:
    1. Create an admin user and log in.
    2. Create a product in the database.
    3. Send a DELETE request for the product.
    4. Assert the response status code and returned product info.

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_admin_user: Factory to create an admin user.
    :type create_admin_user: Callable

    :param create_product_in_db: Factory to create a product in the database.
    :type create_product_in_db: Callable

    :return: None
    """

    user = create_admin_user(email="admin@test.com")

    login = test_client.post("/auth/login", json={"email": user.email, "password": "123456"})
    token = login.json()["access_token"]


    product = create_product_in_db(name="ToDelete", description="Desc", price=1.0, stock=1)

    response = test_client.delete(
        f"/products/{product.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    resp_data = response.json()

    assert resp_data["id"] == product.id
    assert resp_data["name"] == product.name


def test_update_nonexistent_product(test_client: TestClient, create_admin_user: Callable) -> None:
    """
    Test updating a product that does not exist.

    Steps:
    1. Create an admin user and log in.
    2. Attempt to update a product with a non-existent ID.
    3. Assert that the response status code is 404 (Not Found).

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_admin_user: Factory to create an admin user.
    :type create_admin_user: Callable

    :return: None
    """

    user = create_admin_user(email="admin@test.com")
    login = test_client.post("/auth/login", json={"email": user.email, "password": "123456"})
    token = login.json()["access_token"]

    payload = {
        "name": "DoesNotExist",
        "description": "DoesNotExist Description",
        "price": 10,
        "stock": 1
    }

    response = test_client.put("/products/9999", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_delete_nonexistent_product(test_client: TestClient, create_admin_user: Callable) -> None:
    """
    Test deleting a product that does not exist.

    Steps:
    1. Create an admin user and log in.
    2. Attempt to delete a product with a non-existent ID.
    3. Assert that the response status code is 404 (Not Found).

    :param test_client: FastAPI TestClient instance.
    :type test_client: TestClient

    :param create_admin_user: Factory to create an admin user.
    :type create_admin_user: Callable

    :return: None
    """

    user = create_admin_user(email="admin@test.com")
    login_resp = test_client.post(
        "/auth/login",
        json={"email": user.email, "password": "123456"}
    )

    print("Login status code:", login_resp.status_code)
    print("Login response JSON:", login_resp.json())

    login_resp = test_client.post(
        "/auth/login",
        json={"email": user.email, "password": "123456"}
    )

    print("Status code:", login_resp.status_code)
    print("Response JSON:", login_resp.json())

    assert login_resp.status_code == 200, "Login failed, cannot obtain token"

    token = login_resp.json()["access_token"]

    response = test_client.delete(
        "/products/9999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404