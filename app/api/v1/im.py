"""IM 即时通讯 REST API（成员C）

提供好友管理、群组管理、消息历史的 REST 接口。
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.im import (
    MessageSend,
    MessageResponse,
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupMemberAdd,
    GroupMemberResponse,
    ContactAdd,
    ContactResponse,
    OfflineMessageResponse,
)
from app.services.im_service import im_service

router = APIRouter(prefix="/im", tags=["IM 即时通讯"])

# TODO: 集成成员A 的 JWT 认证
# from app.core.deps import get_current_user


# ==================== 联系人/好友 ====================

@router.get("/contacts", response_model=list[ContactResponse], summary="好友列表")
async def list_contacts(
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的好友列表"""
    return await im_service.get_contacts(db, user_id)


@router.post("/contacts", response_model=ContactResponse, summary="添加好友")
async def add_contact(
    data: ContactAdd,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """添加好友（双向好友关系）"""
    contact = await im_service.add_contact(db, user_id, data.contact_user_id, data.alias)
    return contact


@router.delete("/contacts/{contact_id}", summary="删除好友")
async def delete_contact(
    contact_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """删除好友（双向软删除）"""
    success = await im_service.delete_contact(db, user_id, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="联系人不存在")
    return {"message": "删除成功"}


# ==================== 群组 ====================

@router.get("/groups", response_model=list[GroupResponse], summary="我的群列表")
async def list_groups(
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取用户加入的所有群组"""
    return await im_service.get_user_groups(db, user_id)


@router.post("/groups", response_model=GroupResponse, summary="创建群聊")
async def create_group(
    data: GroupCreate,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """创建群聊并添加初始成员"""
    return await im_service.create_group(
        db, group_name=data.group_name, owner_id=user_id,
        avatar_url=data.avatar_url, notice=data.notice,
        member_ids=data.member_ids,
    )


@router.get("/groups/{group_id}", response_model=GroupResponse, summary="群组详情")
async def get_group_detail(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取群组详细信息"""
    group = await im_service.get_group_detail(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="群组不存在")
    return group


@router.put("/groups/{group_id}", response_model=GroupResponse, summary="修改群信息")
async def update_group(
    group_id: int,
    data: GroupUpdate,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """修改群信息（仅群主/管理员可操作）"""
    group = await im_service.update_group(
        db, group_id, user_id, **data.model_dump(exclude_unset=True)
    )
    if not group:
        raise HTTPException(status_code=403, detail="无权操作或群组不存在")
    return group


@router.delete("/groups/{group_id}", summary="解散群")
async def disband_group(
    group_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """解散群聊（仅群主可操作）"""
    success = await im_service.disband_group(db, group_id, user_id)
    if not success:
        raise HTTPException(status_code=403, detail="无权解散或群组不存在")
    return {"message": "群已解散"}


@router.post("/groups/{group_id}/members", summary="添加群成员")
async def add_group_members(
    group_id: int,
    data: GroupMemberAdd,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """添加群成员（仅群主/管理员可操作）"""
    success = await im_service.add_group_members(
        db, group_id, user_id, data.user_type, data.user_ids
    )
    if not success:
        raise HTTPException(status_code=400, detail="添加失败，可能无权限或成员数已达上限")
    return {"message": "添加成功"}


@router.get("/groups/{group_id}/members", response_model=list[GroupMemberResponse], summary="群成员列表")
async def list_group_members(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取群成员列表"""
    return await im_service.get_group_members(db, group_id)


@router.delete("/groups/{group_id}/members/{member_id}", summary="移除群成员")
async def remove_group_member(
    group_id: int,
    member_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """移除群成员（仅群主/管理员可操作）"""
    success = await im_service.remove_group_member(db, group_id, member_id, user_id)
    if not success:
        raise HTTPException(status_code=403, detail="无权操作或成员不存在")
    return {"message": "移除成功"}


@router.post("/groups/{group_id}/leave", summary="退出群聊")
async def leave_group(
    group_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """退出群聊（群主不能退群，需先转让或解散）"""
    success = await im_service.leave_group(db, group_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="退出失败，群主不能退群或群不存在")
    return {"message": "已退出群聊"}


# ==================== 消息历史 ====================

@router.get("/messages/private/{other_user_id}", response_model=OfflineMessageResponse, summary="私聊历史")
async def get_private_history(
    other_user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取私聊历史消息（分页）"""
    messages, total = await im_service.get_private_history(
        db, user_id, other_user_id, page, page_size
    )
    return {"messages": messages, "has_more": (page * page_size) < total}


@router.get("/messages/group/{group_id}", response_model=OfflineMessageResponse, summary="群聊历史")
async def get_group_history(
    group_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """获取群聊历史消息（需要是群成员）"""
    messages, total = await im_service.get_group_history(
        db, group_id, user_id, page, page_size
    )
    return {"messages": messages, "has_more": (page * page_size) < total}


@router.get("/messages/offline", response_model=OfflineMessageResponse, summary="离线消息")
async def get_offline_messages(
    last_msg_id: Optional[int] = Query(None, description="客户端最后一条消息ID"),
    limit: int = Query(50, ge=1, le=100),
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """拉取离线消息（增量同步）"""
    messages, has_more = await im_service.get_offline_messages(db, user_id, last_msg_id, limit)
    return {"messages": messages, "has_more": has_more}


@router.put("/messages/{message_id}/read", summary="标记已读")
async def mark_message_read(
    message_id: int,
    user_id: int = Query(..., description="用户ID（TODO: 从JWT获取）"),
    db: AsyncSession = Depends(get_db),
):
    """标记私聊消息为已读"""
    success = await im_service.mark_message_read(db, message_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")
    return {"message": "已标记已读"}