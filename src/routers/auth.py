from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..db import get_db
from fastapi_jwt_auth import AuthJWT
from ..services.user import get_with_paswd
from ..dependencies import Auth, base_auth, auth_checker, auth_checker_refresh
from ..redis import RedisClient
from ..schemas.auth import LoginOut
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
redis_conn = RedisClient().conn
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token: str) -> bool:
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


@auth_router.post("/login", response_model=LoginOut)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(base_auth)],
):
    db_user = await get_with_paswd(db, form_data)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    user_claims = {"user_claims": {"id": str(db_user.id)}}
    access_token = authorize.create_access_token(
        subject=form_data.username, user_claims=user_claims
    )
    refresh_token = authorize.create_refresh_token(
        subject=form_data.username, user_claims=user_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh")
async def refresh_access_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker_refresh)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    current_user = await authorize.get_current_user(db)
    new_user_claims = {"user_claims": authorize.user_claims}
    new_access_token = authorize.create_access_token(
        subject=current_user.username, user_claims=new_user_claims
    )
    redis_conn.setex(authorize.jti, settings.AUTHJWT_REFRESH_TOKEN_EXPIRES, "true")
    return {"access_token": new_access_token}


@auth_router.delete("/logout", status_code=204)
async def logout(
    authorize: Annotated[Auth, Depends(auth_checker)],
    z: Annotated[str, Depends(oauth2_scheme)],
):
    jti = authorize.jti
    redis_conn.setex(jti, settings.AUTHJWT_ACCESS_TOKEN_EXPIRES, "true")
