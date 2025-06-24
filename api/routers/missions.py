from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from database.schemas import MissionCreate, MissionResponse, MissionAssign, TargetUpdate, TargetResponse
from database.dals import MissionDAL


router = APIRouter(prefix='/missions', tags=['Missions'])

@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    mission: MissionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    return await MissionDAL.create(db, mission)


@router.get("/", response_model=List[MissionResponse])
async def list_missions(db: AsyncSession = Depends(get_db_session)):
    return await MissionDAL.get_all(db)


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    mission = await MissionDAL.get(db, mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    mission_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    success = await MissionDAL.delete(db, mission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )


@router.put("/{mission_id}/assign", response_model=MissionResponse)
async def assign_cat(
    mission_id: int,
    mission_assign: MissionAssign,
    db: AsyncSession = Depends(get_db_session)
):
    return await MissionDAL.assign_cat(db, mission_id, mission_assign.cat_id)


@router.put("/{mission_id}/targets/{target_id}", response_model=TargetResponse)
async def update_target(
    mission_id: int,
    target_id: int,
    target_update: TargetUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    target = await MissionDAL.update_target(db, mission_id, target_id, target_update)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    return target
