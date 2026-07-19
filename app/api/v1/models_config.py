"""F-02: 模型管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, PageResult
from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigListResponse,
    ModelConfigResponse,
    ModelConfigUpdate,
    ModelTestRequest,
    ModelTestResponse,
)
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["模型管理"])


@router.get("", response_model=ApiResponse)
async def list_models(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: str = Query(None, description="模型分类筛选"),
    keyword: str = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取模型列表（分页+搜索）"""
    service = ModelService(db)
    models, total = await service.get_models(
        page=page,
        page_size=page_size,
        category=category,
        keyword=keyword,
    )
    items = [
        ModelConfigListResponse.model_validate(m) for m in models
    ]
    return ApiResponse(data=PageResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    data: ModelConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """添加模型配置"""
    service = ModelService(db)
    model = await service.create_model(data)
    return ApiResponse(
        code=201,
        message="模型创建成功",
        data=ModelConfigResponse.model_validate(model),
    )


@router.get("/{model_id}", response_model=ApiResponse)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取模型详情"""
    service = ModelService(db)
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return ApiResponse(data=ModelConfigResponse.model_validate(model))


@router.put("/{model_id}", response_model=ApiResponse)
async def update_model(
    model_id: int,
    data: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """修改模型配置"""
    service = ModelService(db)
    model = await service.update_model(model_id, data)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return ApiResponse(
        message="模型更新成功",
        data=ModelConfigResponse.model_validate(model),
    )


@router.delete("/{model_id}", response_model=ApiResponse)
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除模型配置（软删除）"""
    service = ModelService(db)
    success = await service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="模型不存在")
    return ApiResponse(message="模型删除成功")


@router.post("/test", response_model=ApiResponse)
async def test_model_connection(
    data: ModelTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """模型连通性测试（不保存到数据库）"""
    success, message = await ModelService.test_connection_direct(
        base_url=data.base_url,
        api_key=data.api_key,
        model_id=data.model_id,
    )
    return ApiResponse(data=ModelTestResponse(success=success, message=message))


@router.put("/{model_id}/default", response_model=ApiResponse)
async def set_default_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """设为默认模型"""
    service = ModelService(db)
    model = await service.set_default(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return ApiResponse(
        message="已设为默认模型",
        data=ModelConfigResponse.model_validate(model),
    )


@router.post("/{model_id}/test", response_model=ApiResponse)
async def test_model_by_id(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """测试已保存模型的连通性"""
    service = ModelService(db)
    try:
        result = await service.test_model(model_id)
        return ApiResponse(data=ModelTestResponse(success=result, message="连接成功" if result else "连接失败"))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return ApiResponse(data=ModelTestResponse(success=False, message=f"连接失败: {str(e)}"))