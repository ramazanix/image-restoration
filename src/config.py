from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_USER_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_URL: str
    AUTHJWT_SECRET_KEY: str
    AUTHJWT_TOKEN_LOCATION: set = {"cookies"}
    AUTHJWT_COOKIE_SECURE: bool
    AUTHJWT_COOKIE_CSRF_PROTECT: bool
    AUTHJWT_DENYLIST_ENABLED: bool
    AUTHJWT_DENYLIST_TOKEN_CHECKS: set = {"access", "refresh"}
    AUTHJWT_COOKIE_MAX_AGE: int
    REDIS_HOST: str
    REDIS_PASSWORD: str

    class Config:
        env_file = "./.env"


settings = Settings()
