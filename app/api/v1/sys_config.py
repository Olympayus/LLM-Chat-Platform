"""System config API (F-SC) — Member F"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.sys_config import SysConfigUpdate, SysConfigResponse
from app.services.sys_config_service import SysConfigService
from app.utils.response import success

router = APIRouter(prefix="/sys-config", tags=["SysConfig"])


@router.get("")
async def get_all_config(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all system configs"""
    service = SysConfigService(db)
    configs = await service.get_all()
    return success(data=[SysConfigResponse.model_validate(c) for c in configs])


@router.get("/{category}")
async def get_config_by_category(category: str, db: AsyncSession = Depends(get_db)):
    """Get configs by category"""
    service = SysConfigService(db)
    configs = await service.get_by_category(category)
    return success(data=[SysConfigResponse.model_validate(c) for c in configs])


@router.put("")
async def update_config(data: SysConfigUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """Upsert a config item"""
    service = SysConfigService(db)
    c = await service.upsert(data.config_key, data.config_value, data.category, data.description)
    return success(data=SysConfigResponse.model_validate(c))


@router.get("/site-info")
async def get_site_info(db: AsyncSession = Depends(get_db)):
    """Get public site info (no auth required)"""
    service = SysConfigService(db)
    return success(data=await service.get_site_info())
