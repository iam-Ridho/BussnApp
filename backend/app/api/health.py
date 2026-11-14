from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.core.db import plain_session

router = APIRouter(prefix="/health", tags=["health"])


class HealthOut(BaseModel):
    status: str


@router.get("", response_model=HealthOut)
async def health() -> HealthOut:
    return HealthOut(status="ok")


@router.get("/db", response_model=HealthOut)
async def health_db() -> HealthOut:
    async with plain_session() as s:
        await s.execute(text("SELECT 1"))
    return HealthOut(status="ok")
