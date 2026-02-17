import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models.accounts import UserGroup, UserGroupEnum


async def seed_groups() -> None:
    async with AsyncSessionLocal() as session:
        for group in UserGroupEnum:
            result = await session.execute(
                select(UserGroup).where(UserGroup.name == group)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                session.add(UserGroup(name=group))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_groups())
