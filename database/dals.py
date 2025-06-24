import logging

from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException

from database.models import *
from database.schemas import *

logger = logging.getLogger(__name__)


class CatDAL:
    """
    Data Access Layer for operating Cat table
    """

    @staticmethod
    async def create(db: AsyncSession, cat: CatCreate) -> Cat:
        db_cat = Cat(**cat.dict())
        db.add(db_cat)
        await db.commit()
        await db.refresh(db_cat)
        return db_cat

    @staticmethod
    async def get(db: AsyncSession, cat_id: int) -> Optional[Cat]:
        result = await db.execute(select(Cat).where(Cat.id == cat_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> Sequence[Cat]:
        result = await db.execute(select(Cat).order_by(Cat.id))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, cat_id: int, cat_update: CatUpdate) -> Optional[Cat]:
        """Update a cat's salary"""
        stmt = (
            update(Cat)
            .where(Cat.id == cat_id)
            .values(**cat_update.dict())
            .returning(Cat)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, cat_id: int) -> bool:
        result = await db.execute(select(Mission).where(Mission.cat_id == cat_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Cannot delete cat with active mission")

        stmt = delete(Cat).where(Cat.id == cat_id)
        result = await db.execute(stmt)
        # TODO: change it
        await db.commit()
        cat = await db.execute(select(Cat).where(Cat.id == cat_id))
        if cat.scalar_one_or_none():
            return False
        return True

    @staticmethod
    async def has_mission(db: AsyncSession, cat_id: int) -> bool:
        result = await db.execute(select(Mission).where(Mission.cat_id == cat_id))
        return result.scalar_one_or_none() is not None

class MissionDAL:
    """
    Data Access Layer for operating Mission table
    """

class TargetDAL:
    """
    Data Access Layer for operating Target table
    """