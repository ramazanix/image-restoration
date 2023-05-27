import os
import aiofiles
from ..security import hash_file_name, process_images, clear_dir
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    BackgroundTasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchema, UserSchemaUpdate
from ..schemas.image import ImageBase
from ..services.user import create, update, delete, get_all, get_by_username
from ..services.image import create as create_img
from ..services.image import delete as delete_img
from ..config import settings
from ..db import get_db
from ..dependencies import Auth, auth_checker
from ..redis import RedisClient
from .auth import oauth2_scheme
from fastapi.concurrency import run_in_threadpool


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
    user: UserSchemaCreate, db: Annotated[AsyncSession, Depends(get_db)]
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


@users_router.post("/upload_image")
async def create_upload_image(
    authorize: Annotated[Auth, Depends(auth_checker)],
    files: list[UploadFile],
    z: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    current_user = await authorize.get_current_user(db)
    files_data = []
    file_dir = f"/tmp/input_images/{current_user.id}"
    clear_dir(file_dir)
    for file in files:
        try:
            filename = hash_file_name(file.filename)
            file_ext = file.filename.split(".")[-1]
            file_content = await file.read()
            if file_ext == "jpeg":
                file_url = f"/static/user_images/{current_user.id}/final_output/{filename}..png"
            else:
                file_url = f"/static/user_images/{current_user.id}/final_output/{filename}.png"
            file_location = os.path.join(file_dir, f"{filename}.{file_ext}")
            os.makedirs(file_dir, exist_ok=True)
            async with aiofiles.open(file_location, "wb+") as image_file:
                file_data = {
                    "name": file.filename,
                    "size": file.size,
                    "location": file_url,
                    "user_id": current_user.id,
                }
                await image_file.write(file_content)
                await create_img(db, file_data)
            files_data.append(
                {
                    "filename": file.filename,
                    "file_size": file.size,
                    "file_location": file_url,
                }
            )
        except Exception:
            await delete_img(db, file_data)
            return {"detail": "Something went wrong"}
        finally:
            await file.close()

    await run_in_threadpool(process_images, file_dir)
    return {
        "files_data": files_data,
        "user": current_user.username,
    }


@users_router.get("/images/results", response_model=list[ImageBase])
async def get_user_images(
    authorize: Annotated[Auth, Depends(auth_checker)],
    z: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    current_user = await authorize.get_current_user(db)
    files_data = current_user.images
    return files_data
