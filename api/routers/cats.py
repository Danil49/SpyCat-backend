from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db_session
from database.schemas import CatCreate, CatUpdate, CatResponse, ErrorResponse
from database.dals import CatDAL
from api.helper import validate_breed_cached, get_cached_breeds

router = APIRouter()

@router.post("/", response_model=CatResponse, status_code=status.HTTP_201_CREATED)
async def create_cat(
        cat: CatCreate,
        db: AsyncSession = Depends(get_db_session)
):
    # Validate breed against Cat API
    if not await validate_breed_cached(cat.breed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid breed: {cat.breed}. Must be a valid cat breed."
        )

    return await CatDAL.create(db, cat)


@router.get("/", response_model=List[CatResponse])
async def list_cats(db: AsyncSession = Depends(get_db_session)):
    return await CatDAL.get_all(db)


@router.get("/{cat_id}", response_model=CatResponse)
async def get_cat(
        cat_id: int,
        db: AsyncSession = Depends(get_db_session)
):
    cat = await CatDAL.get(db, cat_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cat not found"
        )
    return cat


@router.put("/{cat_id}", response_model=CatResponse)
async def update_cat(
        cat_id: int,
        cat_update: CatUpdate,
        db: AsyncSession = Depends(get_db_session)
):
    cat = await CatDAL.update(db, cat_id, cat_update)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cat not found"
        )
    return cat


@router.delete("/{cat_id}", status_code=status.HTTP_200_OK)
async def delete_cat(
        cat_id: int,
        db: AsyncSession = Depends(get_db_session)
):
    success = await CatDAL.delete(db, cat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cat not found"
        )


@router.get("/breeds/valid", response_model=List[str])
async def get_valid_breeds():
    breeds = await get_cached_breeds()
    return [breed["name"] for breed in breeds]
