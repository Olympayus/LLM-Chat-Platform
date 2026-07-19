"""通知中心 API（成员C）

提供通知列表、已读管理、未读计数等接口。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.notification_service import notification_service
from app.utils.response import success, error, paginate

router = APIRouter(prefix="/notifications", tags=["通知中心"])

# TODO: 集成成员A 的 JWT 认证
# from app.core.deps import get_current_user


@router.get("", summary="通知列表（分页）")
async def list_notifications(
    type: Optional[str] = Query(None, description="筛选类型: system/announcement/task/approval"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户通知列表，含已读状态"""
    items, total = await notification_service.get_notifications(
        db, user_id=user_id, type_filter=type, page=page, page_size=page_size
    )
    return paginate(items=items, total=total, page=page, page_size=page_size)


@router.get("/unread-count", summary="未读通知数")
async def get_unread_count(
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户未读通知数量"""
    count = await notification_service.get_unread_count(db, user_id)
    return success(data={"count": count})


@router.get("/{notification_id}", summary="通知详情（自动标记已读）")
async def get_notification(
    notification_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取通知详情并自动标记为已读"""
    detail = await notification_service.get_notification_detail(db, notification_id, user_id)
    if not detail:
        return error(code=404, msg="通知不存在")
    return success(data=detail)


@router.put("/{notification_id}/read", summary="标记已读")
async def mark_read(
    notification_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """标记单条通知为已读"""
    ok = await notification_service.mark_read(db, notification_id, user_id)
    if not ok:
        return error(code=404, msg="通知不存在")
    return success(message="已标记为已读")


@router.put("/read-all", summary="全部标记已读")
async def mark_all_read(
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """标记所有通知为已读"""
    count = await notification_service.mark_all_read(db, user_id)
    return success(data={"marked_count": count}, message=f"已标记 {count} 条通知为已读")