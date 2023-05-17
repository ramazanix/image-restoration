from src.models import Role
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Role]:
    return (await db.execute(sa_select(Role).limit(bound))).scalars().all()
