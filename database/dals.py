import logging

from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from database.models import *
from database.models import Mission
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

    @staticmethod
    async def create(db: AsyncSession, mission: MissionCreate) -> Mission:
        # Check if cat already has a mission
        existing_mission = await CatDAL.has_mission(db, mission.cat_id)
        if existing_mission:
            raise HTTPException(status_code=400, detail="Cat already has a mission")

        # Create mission
        db_mission = Mission(cat_id=mission.cat_id)
        db.add(db_mission)
        await db.flush()  # Get the mission ID

        # Create targets
        for target_data in mission.targets:
            db_target = Target(
                mission_id=db_mission.id,
                **target_data.dict()
            )
            db.add(db_target)

        await db.commit()
        await db.refresh(db_mission)

        # Load targets with mission
        stmt = select(Mission).options(selectinload(Mission.targets)).where(Mission.id == db_mission.id)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get(db: AsyncSession, mission_id: int) -> Optional[Mission]:
        stmt = (
            select(Mission)
            .options(selectinload(Mission.targets))
            .where(Mission.id == mission_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> Sequence[Mission]:
        stmt = select(Mission).options(selectinload(Mission.targets)).order_by(Mission.id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def delete(db: AsyncSession, mission_id: int) -> bool:
        # Check if mission is assigned to a cat
        mission = await MissionDAL.get(db, mission_id)
        if not mission:
            return False

        if mission.cat_id:
            raise HTTPException(status_code=400, detail="Cannot delete mission that is assigned to a cat")

        result = await db.execute(delete(Mission).where(Mission.id == mission_id))
        # TODO: change it
        await db.commit()
        cat = await db.execute(select(Cat).where(Mission.id == mission_id))
        if cat.scalar_one_or_none():
            return False
        return True

    @staticmethod
    async def assign_cat(db: AsyncSession, mission_id: int, cat_id: int) -> Optional[Mission]:
        """Assign a cat to an existing unassigned mission"""
        # Check if cat already has a mission
        if await CatDAL.has_mission(db, cat_id):
            raise HTTPException(status_code=400, detail="Cat already has a mission")

        # Check if mission exists and is unassigned
        mission = await MissionDAL.get(db, mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        if mission.cat_id:
            raise HTTPException(status_code=400, detail="Mission is already assigned to a cat")

        # Assign cat
        stmt = (
            update(Mission)
            .where(Mission.id == mission_id)
            .values(cat_id=cat_id)
            .returning(Mission)
        )
        result = await db.execute(stmt)
        await db.commit()

        return await MissionDAL.get(db, mission_id)

    @staticmethod
    async def update_target(db: AsyncSession, mission_id: int, target_id: int, target_update: TargetUpdate) -> Optional[Target]:
        """Update a target within a mission"""
        # Get mission and target
        mission = await MissionDAL.get(db, mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        if mission.complete:
            raise HTTPException(status_code=400, detail="Cannot update target in completed mission")

        # Get target
        stmt = select(Target).where(and_(Target.id == target_id, Target.mission_id == mission_id))
        result = await db.execute(stmt)
        target = result.scalar_one_or_none()

        if not target:
            raise HTTPException(status_code=404, detail="Target not found")

        if target.complete and target_update.notes is not None:
            raise HTTPException(status_code=400, detail="Cannot update notes for completed target")

        # Update target
        update_data = target_update.dict(exclude_unset=True)
        stmt = (
            update(Target)
            .where(Target.id == target_id)
            .values(**update_data)
            .returning(Target)
        )
        result = await db.execute(stmt)
        updated_target = result.scalar_one_or_none()

        # Check if mission should be marked complete
        if updated_target and updated_target.complete:
            await MissionDAL._check_and_complete_mission(db, mission_id)

        await db.commit()
        return updated_target

    @staticmethod
    async def _check_and_complete_mission(db: AsyncSession, mission_id: int):
        stmt = select(Target).where(Target.mission_id == mission_id)
        result = await db.execute(stmt)
        targets = result.scalars().all()

        if all(target.complete for target in targets):
            await db.execute(
                update(Mission)
                .where(Mission.id == mission_id)
                .values(complete=True)
            )

