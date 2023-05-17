from src.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from ..schemas.user import UserSchemaCreate, UserSchemaUpdate
from ..security import get_password_hash, verify_password
from collections.abc import Sequence


async def create(db: AsyncSession, user: UserSchemaCreate) -> User | None:
    if await get_by_username(db, user.username):
        return None
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update(db: AsyncSession, payload: UserSchemaUpdate, user: User) -> User:
    update_data = payload.dict(exclude_none=True, exclude_unset=True)
    if update_data.get("password"):
        hashed_passwd = get_password_hash(update_data.get("password"))
        update_data["hashed_password"] = hashed_passwd
        update_data.pop("password")

    query = sa_update(User).where(User.username == user.username).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def get_with_paswd(db: AsyncSession, user: UserSchemaCreate) -> User | None:
    try:
        db_user = (
            await db.execute(sa_select(User).where((User.username == user.username)))
        ).scalar()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise NoResultFound
        return db_user
    except NoResultFound:
        return None


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    return (
        await db.execute(sa_select(User).where(User.username == username))
    ).scalar_one_or_none()


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[User]:
    return (
        (await db.execute(sa_select(User).limit(bound).order_by(User.created_at)))
        .scalars()
        .all()
    )


async def get_by_id(db: AsyncSession, user_id: int | str) -> User | None:
    return await db.get(User, user_id)
