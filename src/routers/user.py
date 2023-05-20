from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchema, UserSchemaUpdate
from ..services.user import create, update, delete, get_all, get_by_username
from ..config import settings
from ..db import get_db
from ..dependencies import Auth, auth_checker
from ..redis import RedisClient
from .auth import oauth2_scheme


users_router = APIRouter(prefix="/users", tags=["Users"])
redis_conn = RedisClient().conn


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    return await authorize.get_current_user(db)


@users_router.post("", response_model=UserSchema, status_code=201)
async def create_user(
    user: UserSchemaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    new_user = await create(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@users_router.get("", response_model=list[UserSchema])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(None, gt=0),
):
    return await get_all(db, limit)


@users_router.get(
    "/{username}", response_model=UserSchema, dependencies=[Depends(auth_checker)]
)
async def get_user(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    user = await get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@users_router.patch("/{username}", response_model=UserSchema)
async def update_user(
    username: str,
    payload: UserSchemaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    current_user = await authorize.get_current_user(db)
    if not existed_user.id == current_user.id:
        raise HTTPException(status_code=405)

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    return await update(db, payload, existed_user)


@users_router.delete("/{username}", status_code=204)
async def delete_user(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    current_user = await authorize.get_current_user(db)
    if not existed_user.id == current_user.id:
        raise HTTPException(status_code=405)

    redis_conn.setex(authorize.jti, settings.AUTHJWT_COOKIE_MAX_AGE, "true")
    authorize.unset_jwt_cookies()
    return await delete(db, existed_user)
