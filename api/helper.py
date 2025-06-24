from typing import List
import httpx
from fastapi import HTTPException
from config import Config

class CatAPI:
    @classmethod
    async def get_breeds(cls) -> List[dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{Config.VALIDATE_URL}/breeds", timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"External API unavailable: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=503, detail=f"External API error: {str(e)}")

    @classmethod
    async def validate_breed(cls, breed: str) -> bool:
        breeds = await cls.get_breeds()
        breed_names = [breed["name"].lower() for breed in breeds]
        return breed.lower() in breed_names

    @classmethod
    async def get_valid_breeds(cls) -> List[str]:
        breeds = await cls.get_breeds()
        return [breed["name"] for breed in breeds]


# Cached breeds
_breeds_cache = None
_cache_timestamp = None


async def get_cached_breeds() -> List[dict]:
    global _breeds_cache, _cache_timestamp
    import time

    # Cache for 1 hour
    if _breeds_cache is None or (time.time() - _cache_timestamp) > 3600:
        _breeds_cache = await CatAPI.get_breeds()
        _cache_timestamp = time.time()

    return _breeds_cache


async def validate_breed_cached(breed: str) -> bool:
    breeds = await get_cached_breeds()
    breed_names = [breed["name"].lower() for breed in breeds]
    return breed.lower() in breed_names
