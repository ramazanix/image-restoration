from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_USER_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_URL: str
    AUTHJWT_SECRET_KEY: str
    AUTHJWT_DENYLIST_ENABLED: bool
    AUTHJWT_DENYLIST_TOKEN_CHECKS: set = {"access", "refresh"}
    AUTHJWT_ACCESS_TOKEN_EXPIRES: int
    AUTHJWT_REFRESH_TOKEN_EXPIRES: int
    REDIS_HOST: str
    REDIS_PASSWORD: str

    class Config:
        env_file = "./.env"


settings = Settings()
