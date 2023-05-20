from pydantic import BaseModel


class LoginOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshOut(BaseModel):
    refresh_token: str
