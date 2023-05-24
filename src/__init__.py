from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.config import settings
from src.db import session_manager
from src.redis import RedisClient


def init_app(init_db=True):
    lifespan = None

    if init_db:
        session_manager.init(settings.DB_URL)
        RedisClient(settings.REDIS_HOST, settings.REDIS_PASSWORD)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if session_manager._engine is not None:
                await session_manager.close()

    server = FastAPI(title="Photo Restoration", lifespan=lifespan)

    from .routers.auth import auth_router
    from .routers.user import users_router
    from .routers.role import roles_router
    from .handlers import auth_jwt_exception_handler
    from fastapi_jwt_auth.exceptions import AuthJWTException
    from fastapi.middleware.cors import CORSMiddleware

    origins = [
        "http://localhost:3000",
    ]

    server.include_router(auth_router, prefix='/api')
    server.include_router(users_router, prefix='/api')
    server.include_router(roles_router, prefix='/api')
    server.add_exception_handler(AuthJWTException, auth_jwt_exception_handler)
    server.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    server.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")

    return server
