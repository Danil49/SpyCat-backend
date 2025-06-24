from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Cat schemas
class CatBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    years_of_experience: int = Field(..., ge=0)
    specialization: str = Field(..., min_length=1, max_length=100)
    salary: float = Field(..., gt=0)


class CatCreate(CatBase):
    pass


class CatUpdate(BaseModel):
    salary: float = Field(..., gt=0)


class CatResponse(CatBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Target schemas
class TargetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=1, max_length=100)
    notes: str = Field(default="")


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    notes: Optional[str] = None
    complete: Optional[bool] = None


class TargetResponse(TargetBase):
    id: int
    complete: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Mission schemas
class MissionBase(BaseModel):
    cat_id: Optional[int] = None


class MissionCreate(BaseModel):
    """Schema for creating mission with targets"""
    cat_id: int
    targets: List[TargetCreate] = Field(..., min_items=1, max_items=3)

    @field_validator('targets')
    def validate_targets_count(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError('Mission must have 1 to 3 targets')
        return v


class MissionAssign(BaseModel):
    """Schema for assigning a cat to an existing mission"""
    cat_id: int


class MissionResponse(MissionBase):
    id: int
    complete: bool
    targets: List[MissionBase] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Error schemas
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""
    detail: str
    errors: Optional[List[dict]] = None
