"""F-05: 技能管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, PageResult
from app.schemas.skill import (
    SkillCreate,
    SkillListItem,
    SkillResponse,
    SkillUpdate,
    SkillAiGenerateRequest,
    SkillAiGenerateResponse,
    SkillTestResponse,
)
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["技能管理"])


@router.get("", response_model=ApiResponse)
async def list_skills(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: str = Query(None, description="分类标签"),
    skill_type: str = Query(None, alias="type", description="技能类型"),
    keyword: str = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取技能列表（分页+搜索）"""
    service = SkillService(db)
    skills, total = await service.get_skills(
        page=page,
        page_size=page_size,
        category=category,
        skill_type=skill_type,
        keyword=keyword,
    )
    items = [SkillListItem.model_validate(s) for s in skills]
    return ApiResponse(data=PageResult(items=items, total=total, page=page, page_size=page_size))


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """手动创建技能"""
    service = SkillService(db)
    skill = await service.create_skill(data, created_by=current_user.id)
    return ApiResponse(code=201, message="技能创建成功", data=SkillResponse.model_validate(skill))


@router.get("/{skill_id}", response_model=ApiResponse)
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取技能详情"""
    service = SkillService(db)
    skill = await service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return ApiResponse(data=SkillResponse.model_validate(skill))


@router.put("/{skill_id}", response_model=ApiResponse)
async def update_skill(
    skill_id: int,
    data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """修改技能"""
    service = SkillService(db)
    skill = await service.update_skill(skill_id, data)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return ApiResponse(message="技能更新成功", data=SkillResponse.model_validate(skill))


@router.delete("/{skill_id}", response_model=ApiResponse)
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除技能（软删除）"""
    service = SkillService(db)
    success = await service.delete_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail="技能不存在")
    return ApiResponse(message="技能删除成功")


@router.post("/ai-generate", response_model=ApiResponse)
async def ai_generate_skill(
    data: SkillAiGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """AI 辅助生成技能"""
    service = SkillService(db)
    try:
        result = await service.ai_generate_skill(
            requirement=data.requirement,
            model_id=data.model_id,
            skill_type=data.skill_type,
        )
        return ApiResponse(message="AI 生成技能完成", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失败: {str(e)}")


@router.post("/{skill_id}/test", response_model=ApiResponse)
async def test_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """测试技能 — 在沙箱中执行技能代码"""
    service = SkillService(db)
    try:
        success, result = await service.test_skill(skill_id)
        return ApiResponse(data=SkillTestResponse(success=success, result=result))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{skill_id}/params", response_model=ApiResponse)
async def get_skill_params(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取技能参数列表"""
    service = SkillService(db)
    skill = await service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    params = await service.get_skill_params(skill_id)
    return ApiResponse(data=params)