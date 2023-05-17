from fastapi import HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_jwt_auth import AuthJWT
from .models import User
from .config import settings
from .services.user import get_by_id


@AuthJWT.load_config
def get_config():
    return settings


class Auth(AuthJWT):
    def __init__(self, check_token: bool = True, refresh: bool = False):
        super().__init__()
        self.raw_jwt = None
        self.jti = None
        self.user_claims = None
        self.check_token = check_token
        self._refresh = refresh

    def __call__(self, req: Request = None, res: Response = None):
        super().__init__(req, res)
        if self.check_token:
            if self._refresh:
                self.jwt_refresh_token_required()
            else:
                self.jwt_required()

            self.raw_jwt = self.get_raw_jwt()
            self.jti = self.raw_jwt.get("jti")
            self.user_claims = self.raw_jwt.get("user_claims")
        return self

    async def get_current_user(self, db: AsyncSession) -> User:
        user_id = self.user_claims["id"]
        user = await get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


base_auth = Auth(check_token=False)
auth_checker = Auth()
auth_checker_refresh = Auth(refresh=True)
