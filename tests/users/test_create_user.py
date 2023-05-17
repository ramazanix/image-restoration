import pytest
from httpx import AsyncClient
from pytest_schema import exact_schema
from .schemas import user, users


user_data = {"username": "Paul", "password": "paul_password"}


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """
    Trying to create user
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201

    assert exact_schema(user) == response.json()

    assert response.json().get("username") == user_data["username"]


@pytest.mark.asyncio
async def test_create_couple_users(client: AsyncClient):
    """
    Trying to create a couple of users
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post(
        "/users", json={"username": "Tom", "password": "tom_password"}
    )

    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == "Tom"

    response = await client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert exact_schema(users) == response.json()


@pytest.mark.asyncio
async def test_create_blank_body(client: AsyncClient):
    """
    Trying to send request with blank body
    """
    response = await client.post("/users", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_invalid_user_data(client: AsyncClient):
    """
    Trying to send invalid body content
    """
    response = await client.post("/users", json={"a": "b"})
    assert response.status_code == 422

    response = await client.post("/users", json={"username": ""})
    assert response.status_code == 422

    response = await client.post("/users", json={"password": ""})
    assert response.status_code == 422

    response = await client.post("/users", json={"username": "", "password": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_short_username(client: AsyncClient):
    """
    Trying to create user with too short username
    """
    response = await client.post(
        "/users", json={"username": "u", "password": "password"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_long_username(client: AsyncClient):
    """
    Trying to create user with too long username
    """
    response = await client.post(
        "/users", json={"username": "me" * 21, "password": "password"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_short_password(client: AsyncClient):
    """
    Trying to create user with too short password
    """
    response = await client.post("/users", json={"username": "Alex", "password": "123"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_long_password(client: AsyncClient):
    """
    Trying to create user with too long password
    """
    response = await client.post(
        "/users", json={"username": "Alex", "password": "123" * 11}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_short_fields(client: AsyncClient):
    """
    Trying to create user with too short username and password
    """
    response = await client.post("/users", json={"username": "u", "password": "passwd"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_long_fields(client: AsyncClient):
    """
    Trying to create user with too long username and password
    """
    response = await client.post(
        "/users", json={"username": "Joe" * 10, "password": "passwd" * 6}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_existing_user(client: AsyncClient):
    """
    Trying to create existing user
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert exact_schema(user) == response.json()
    assert response.json().get("username") == user_data["username"]

    response = await client.post("/users", json=user_data)
    assert response.status_code == 400
    assert response.json().get("detail") == "User already exists"
