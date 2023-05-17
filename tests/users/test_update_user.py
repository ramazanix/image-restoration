import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user
from ..auth.schemas import success, error


user_data = {"username": "Alex", "password": "alex_password"}

correct_cookies: list[str] = [
    "access_token_cookie",
    "csrf_access_token",
    "csrf_refresh_token",
    "refresh_token_cookie",
]


@pytest.mark.asyncio
async def test_update_user_unauthorized(client: AsyncClient):
    """
    Trying to update user without auth
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.patch(
        f"/users/{user_data['username']}", json={"username": "not_Alex"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_authorized(client: AsyncClient):
    """
    Trying to update user with auth
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch(
        "/users/Alex", json={"username": "not_Alex"}, headers=headers
    )
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_Alex"

    response = await client.get(f"/users/{user_data['username']}", headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "User not found"

    response = await client.get("/users/not_Alex", headers=headers)
    assert response.status_code == 200
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "not_Alex"


@pytest.mark.asyncio
async def test_update_user_blank_body(client: AsyncClient):
    """
    Trying to update user with blank body
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch(
        f"/users/{user_data['username']}", json={}, headers=headers
    )

    assert response.status_code == 400
    assert exact_schema(error) == response.json()
    assert response.json().get("detail") == "Bad Request"


@pytest.mark.asyncio
async def test_update_user_too_small_username(client: AsyncClient):
    """
    Trying to update user's username to small value
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch("/users/Joe", json={"username": "J"}, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_username(client: AsyncClient):
    """
    Trying to update user's username to long value
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch(
        "/users/Alex", json={"username": "A" * 21}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_small_password(client: AsyncClient):
    """
    Trying to update user's password to small value
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch(
        "/users/Alex", json={"password": "A" * 33}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_too_long_password(client: AsyncClient):
    """
    Trying to update user's password to long value
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch(
        "/users/Alex", json={"password": "A" * 33}, headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_invalid_body(client: AsyncClient):
    """
    Trying to update user with invalid body
    """
    user_data = {"username": "username", "password": "password"}
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "username"

    response = await client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    assert exact_schema(success) == response.json()
    assert list(response.cookies.keys()) == correct_cookies

    cookies = response.cookies
    headers = {"X-CSRF-Token": cookies.get("csrf_access_token")}

    response = await client.patch("/users/username", json={"a": "b"}, headers=headers)
    assert response.status_code == 400
    assert response.json().get("detail") == "Bad Request"

    response = await client.patch(
        "/users/username", json={"username": "", "password": ""}, headers=headers
    )
    assert response.status_code == 422

    response = await client.patch(
        "/users/username",
        json={"username": "username", "password": ""},
        headers=headers,
    )
    assert response.status_code == 422
