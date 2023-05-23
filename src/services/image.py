from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Image


async def create(db: AsyncSession, image: dict[str, str | int]) -> Image | None:
    db_image = Image(**image)
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    return db_image
