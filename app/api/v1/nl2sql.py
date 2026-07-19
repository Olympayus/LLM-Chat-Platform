"""NL2SQL 智能问数 API 路由

端点:
- POST   /api/v1/nl2sql/ask              — 智能问数
- GET    /api/v1/nl2sql/schema            — 获取数据库 Schema
- GET    /api/v1/nl2sql/history           — 查询历史列表
- GET    /api/v1/nl2sql/history/{id}      — 查询历史详情
- DELETE /api/v1/nl2sql/history           — 删除查询历史
- POST   /api/v1/nl2sql/favorites         — 创建收藏
- GET    /api/v1/nl2sql/favorites         — 收藏列表
- DELETE /api/v1/nl2sql/favorites/{id}    — 取消收藏
- PUT    /api/v1/nl2sql/favorites/{id}    — 更新收藏备注
- POST   /api/v1/nl2sql/validate          — 校验 SQL
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.sandbox.sql_validator import sql_validator
from app.schemas.nl2sql import (
    DeleteHistoryRequest,
    FavoriteCreateRequest,
    FavoriteListRequest,
    FavoriteUpdateRequest,
    Nl2sqlAskRequest,
    QueryHistoryListRequest,
    SchemaInfoRequest,
    SqlValidationResult,
)
from app.services.nl2sql_service import nl2sql_service
from app.utils.response import error, paginate, success

router = APIRouter(prefix="/api/v1/nl2sql", tags=["NL2SQL 智能问数"])


# ==================== 核心问数 ====================


@router.post("/ask", summary="智能问数")
async def ask(
    request: Nl2sqlAskRequest,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """使用自然语言提问，返回 AI 生成的 SQL 和查询结果"""
    user_id = int(current_user.get("sub", 0))

    try:
        result = await nl2sql_service.ask(
            request=request,
            user_id=user_id,
            db=db,
        )
        return success(data=result.model_dump())
    except Exception as e:
        return error(message=f"问数失败: {str(e)}")


@router.post("/validate", summary="校验 SQL")
async def validate_sql(
    sql_request: dict,
):
    """安全校验 SQL 语句（不执行）"""
    sql = sql_request.get("sql", "")
    result = sql_validator.validate(sql)
    return success(data=result.model_dump())


# ==================== Schema 信息 ====================


@router.get("/schema", summary="获取数据库 Schema")
async def get_schema(
    database_name: str = Query("llm_platform", description="数据库名"),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """获取数据库表结构信息"""
    try:
        result = await nl2sql_service.get_schema_info(
            database_name=database_name,
            db=db,
        )
        return success(data=result)
    except Exception as e:
        return error(message=f"获取 Schema 失败: {str(e)}")


# ==================== 查询历史 ====================


@router.get("/history", summary="查询历史列表")
async def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """获取当前用户的查询历史列表"""
    user_id = int(current_user.get("sub", 0))

    try:
        result = await nl2sql_service.get_history(
            user_id=user_id,
            page=page,
            page_size=page_size,
            keyword=keyword,
            db=db,
        )
        return paginate(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as e:
        return error(message=f"获取历史失败: {str(e)}")


@router.get("/history/{history_id}", summary="查询历史详情")
async def get_history_detail(
    history_id: int,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """获取指定查询历史的详细信息"""
    user_id = int(current_user.get("sub", 0))

    try:
        detail = await nl2sql_service.get_history_detail(
            history_id=history_id,
            user_id=user_id,
            db=db,
        )
        if detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="查询历史不存在",
            )
        return success(data=detail)
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"获取详情失败: {str(e)}")


@router.delete("/history", summary="删除查询历史")
async def delete_history(
    request: DeleteHistoryRequest,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """批量删除查询历史"""
    user_id = int(current_user.get("sub", 0))

    try:
        deleted_count = await nl2sql_service.delete_history(
            ids=request.ids,
            user_id=user_id,
            db=db,
        )
        return success(
            data={"deleted_count": deleted_count},
            message=f"成功删除 {deleted_count} 条记录",
        )
    except Exception as e:
        return error(message=f"删除失败: {str(e)}")


# ==================== 收藏 ====================


@router.post("/favorites", summary="创建收藏")
async def create_favorite(
    request: FavoriteCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """收藏查询历史"""
    user_id = int(current_user.get("sub", 0))

    try:
        favorite = await nl2sql_service.create_favorite(
            request=request,
            user_id=user_id,
            db=db,
        )
        if favorite is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="查询历史不存在",
            )
        return success(data=favorite, message="收藏成功")
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"收藏失败: {str(e)}")


@router.get("/favorites", summary="收藏列表")
async def get_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """获取当前用户的收藏列表"""
    user_id = int(current_user.get("sub", 0))

    try:
        result = await nl2sql_service.get_favorites(
            user_id=user_id,
            page=page,
            page_size=page_size,
            db=db,
        )
        return paginate(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )
    except Exception as e:
        return error(message=f"获取收藏失败: {str(e)}")


@router.delete("/favorites/{favorite_id}", summary="取消收藏")
async def delete_favorite(
    favorite_id: int,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """取消收藏"""
    user_id = int(current_user.get("sub", 0))

    try:
        success_flag = await nl2sql_service.delete_favorite(
            favorite_id=favorite_id,
            user_id=user_id,
            db=db,
        )
        if not success_flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏不存在",
            )
        return success(message="取消收藏成功")
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"取消收藏失败: {str(e)}")


@router.put("/favorites/{favorite_id}", summary="更新收藏备注")
async def update_favorite_note(
    favorite_id: int,
    request: FavoriteUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db),
):
    """更新收藏的备注信息"""
    user_id = int(current_user.get("sub", 0))

    try:
        favorite = await nl2sql_service.update_favorite_note(
            favorite_id=favorite_id,
            note=request.note or "",
            user_id=user_id,
            db=db,
        )
        if favorite is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏不存在",
            )
        return success(data=favorite, message="更新成功")
    except HTTPException:
        raise
    except Exception as e:
        return error(message=f"更新失败: {str(e)}")