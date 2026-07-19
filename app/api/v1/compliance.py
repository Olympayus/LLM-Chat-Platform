"""合规审计 API 路由（F-08）

包含:
- 敏感词管理
- 消息管理（搜索、撤回、导出）
- 群组管控
- 用户处置
- 审计日志查询

权限说明:
- admin: 系统管理员
- auditor: 审计员
- super_admin: 超级管理员

TODO: 需要集成成员A 的 JWT 认证中间件进行权限控制
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.im import (
    SensitiveWordCreate,
    SensitiveWordUpdate,
    SensitiveWordResponse,
    AuditLogResponse,
    AuditLogSearchRequest,
    MessageSearchRequest,
    MessageSearchResponse,
    MessageRecallRequest,
    GroupSystemMessageRequest,
    GroupListResponse,
    GroupDetailResponse,
    MuteUserRequest,
    BanUserRequest,
    PageResult,
)
from app.services.compliance_service import compliance_service

router = APIRouter(prefix="/admin", tags=["合规审计"])

# TODO: 后续集成成员A 的权限注入
# from app.core.deps import get_current_user, require_role


# ==================== 敏感词管理 ====================

@router.get("/sensitive-words", response_model=PageResult, summary="敏感词列表")
async def list_sensitive_words(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取敏感词列表（分页）"""
    return await compliance_service.get_words(db, page=page, page_size=page_size)


@router.post("/sensitive-words", response_model=SensitiveWordResponse, summary="添加敏感词")
async def create_sensitive_word(
    data: SensitiveWordCreate,
    db: AsyncSession = Depends(get_db),
):
    """添加敏感词"""
    # TODO: 从 JWT 获取当前用户ID
    word = await compliance_service.create_word(db, data, created_by=0)
    return word


@router.put("/sensitive-words/{word_id}", response_model=SensitiveWordResponse, summary="修改敏感词")
async def update_sensitive_word(
    word_id: int,
    data: SensitiveWordUpdate,
    db: AsyncSession = Depends(get_db),
):
    """修改敏感词"""
    word = await compliance_service.update_word(db, word_id, data)
    if not word:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    return word


@router.delete("/sensitive-words/{word_id}", summary="删除敏感词")
async def delete_sensitive_word(
    word_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除敏感词"""
    success = await compliance_service.delete_word(db, word_id)
    if not success:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    return {"message": "删除成功"}


# ==================== 群组管控 ====================

@router.get("/groups", summary="全平台群组列表")
async def list_groups(
    keyword: str = Query(None, description="群名称搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取全平台群组列表（管理端）"""
    return await compliance_service.get_all_groups(
        db, keyword=keyword, page=page, page_size=page_size
    )


@router.get("/groups/{group_id}", summary="群组详情 + 成员")
async def get_group_detail(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取群组详情及成员列表"""
    detail = await compliance_service.get_group_detail(db, group_id)
    if not detail:
        raise HTTPException(status_code=404, detail="群组不存在")
    return detail


@router.delete("/groups/{group_id}/members/{member_id}", summary="强制移除群成员")
async def remove_group_member(
    group_id: int,
    member_id: int,
    db: AsyncSession = Depends(get_db),
):
    """强制移除群成员"""
    # [F-01] 由成员A负责接入JWT后替换
    # 预期接口: get_current_user() -> SysUser
    # current_user = await get_current_user(request)
    success = await compliance_service.remove_member(db, group_id, member_id, admin_id=0)
    if not success:
        raise HTTPException(status_code=404, detail="成员或群组不存在")
    return {"message": "移除成功"}


@router.put("/groups/{group_id}/mute-all", summary="全员禁言开关")
async def toggle_mute_all(
    group_id: int,
    is_muted: bool = Query(..., description="是否全员禁言"),
    db: AsyncSession = Depends(get_db),
):
    """开启或关闭全员禁言"""
    # [F-01] 由成员A负责接入JWT后替换
    # 预期接口: get_current_user() -> SysUser
    # current_user = await get_current_user(request); admin_id = current_user.id
    success = await compliance_service.mute_all(db, group_id, is_muted, admin_id=0)
    if not success:
        raise HTTPException(status_code=404, detail="群组不存在")
    return {"message": "全员禁言已更新"}


@router.put("/groups/{group_id}/bot-toggle", summary="开关数字员工应答")
async def toggle_bot(
    group_id: int,
    enabled: bool = Query(..., description="是否启用数字员工"),
    db: AsyncSession = Depends(get_db),
):
    """开关群聊中的数字员工应答"""
    # [F-01] 由成员A负责接入JWT后替换
    # 预期接口: get_current_user() -> SysUser
    # current_user = await get_current_user(request); admin_id = current_user.id
    success = await compliance_service.toggle_bot(db, group_id, enabled, admin_id=0)
    if not success:
        raise HTTPException(status_code=404, detail="群组不存在")
    return {"message": "数字员工应答已更新"}


@router.post("/groups/{group_id}/system-msg", summary="发送系统消息")
async def send_system_message(
    group_id: int,
    data: GroupSystemMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """向群内发送系统消息（管理员公告）"""
    # [F-01] 由成员A负责接入JWT后替换 admin_id
    # [F-07/C] 由成员C提供 ws_manager 实例
    # 预期接口: get_current_user() -> SysUser; ws_manager = ConnectionManager()
    success = await compliance_service.send_system_message(
        db, group_id, data.content, admin_id=0, ws_manager=None
    )
    if not success:
        raise HTTPException(status_code=404, detail="群组不存在")
    return {"message": "系统消息已发送"}


@router.delete("/groups/{group_id}", summary="解散群")
async def dismiss_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """解散群聊"""
    # [F-01] 由成员A负责接入JWT后替换
    # 预期接口: get_current_user() -> SysUser
    # current_user = await get_current_user(request); admin_id = current_user.id
    success = await compliance_service.dismiss_group(db, group_id, admin_id=0)
    if not success:
        raise HTTPException(status_code=404, detail="群组不存在")
    return {"message": "群已解散"}


# ==================== 消息管理 ====================

@router.get("/messages/search", summary="穿透查询聊天记录")
async def search_messages(
    keyword: str = Query(None, description="关键词"),
    sender_id: int = Query(None, description="发送者ID"),
    group_id: int = Query(None, description="群组ID"),
    chat_type: str = Query(None, pattern="^(private|group)$", description="会话类型"),
    start_time: str = Query(None, description="开始时间(ISO格式)"),
    end_time: str = Query(None, description="结束时间(ISO格式)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """多条件搜索聊天记录（走 ES 搜索引擎）"""
    from datetime import datetime

    query = MessageSearchRequest(
        keyword=keyword,
        sender_id=sender_id,
        group_id=group_id,
        chat_type=chat_type,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        page=page,
        page_size=page_size,
    )
    return await compliance_service.search_messages(query)


@router.post("/messages/{message_id}/recall", summary="强制撤回消息")
async def recall_message(
    message_id: int,
    data: MessageRecallRequest = MessageRecallRequest(),
    db: AsyncSession = Depends(get_db),
):
    """强制撤回某条消息（MySQL 标记 + ES 删除 + WS 广播）"""
    # [F-01] 由成员A负责接入JWT后替换 admin_id
    # [F-07/C] 由成员C提供 ws_manager 实例
    # 预期接口: get_current_user() -> SysUser; ws_manager = ConnectionManager()
    success = await compliance_service.recall_message(
        db, message_id, admin_id=0, reason=data.reason, ws_manager=None
    )
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")
    return {"message": "消息已撤回"}


@router.post("/messages/export/pdf", summary="导出聊天记录为 PDF")
async def export_messages_pdf(
    keyword: str = Query(None),
    sender_id: int = Query(None),
    group_id: int = Query(None),
    start_time: str = Query(None),
    end_time: str = Query(None),
):
    """导出聊天记录为 PDF 格式"""
    from datetime import datetime

    query = MessageSearchRequest(
        keyword=keyword,
        sender_id=sender_id,
        group_id=group_id,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        page=1,
        page_size=10000,
    )
    content = await compliance_service.export_messages(query, export_format="pdf")
    return content


@router.post("/messages/export/excel", summary="导出聊天记录为 Excel")
async def export_messages_excel(
    keyword: str = Query(None),
    sender_id: int = Query(None),
    group_id: int = Query(None),
    start_time: str = Query(None),
    end_time: str = Query(None),
):
    """导出聊天记录为 Excel 格式"""
    from datetime import datetime

    query = MessageSearchRequest(
        keyword=keyword,
        sender_id=sender_id,
        group_id=group_id,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        page=1,
        page_size=10000,
    )
    content = await compliance_service.export_messages(query, export_format="excel")
    return content


# ==================== 用户处置 ====================

@router.put("/users/{user_id}/mute", summary="禁言用户")
async def mute_user(
    user_id: int,
    data: MuteUserRequest,
    db: AsyncSession = Depends(get_db),
):
    """禁言用户（存储在 Redis 中，有自动过期时间）"""
    # [F-01] 由成员A负责接入JWT后替换 admin_id
    # 预期接口: get_current_user() -> SysUser; admin_id = current_user.id
    success = await compliance_service.mute_user(db, user_id, data.duration_minutes, admin_id=0)
    if not success:
        raise HTTPException(status_code=400, detail="禁言失败")
    return {"message": f"用户已禁言 {data.duration_minutes} 分钟"}


@router.put("/users/{user_id}/ban", summary="封号")
async def ban_user(
    user_id: int,
    data: BanUserRequest = BanUserRequest(),
    db: AsyncSession = Depends(get_db),
):
    """封禁用户账号"""
    # [F-01] 由成员A负责接入JWT后替换 admin_id
    # 预期接口: get_current_user() -> SysUser; admin_id = current_user.id
    # 另需成员A配合: await db.execute(update(SysUser).where(SysUser.id == user_id).values(status=2))
    success = await compliance_service.ban_user(db, user_id, data.reason, admin_id=0)
    if not success:
        raise HTTPException(status_code=400, detail="封号失败")
    return {"message": "用户已封号"}


# ==================== 审计日志 ====================

@router.get("/audit-logs", summary="审计日志列表")
async def list_audit_logs(
    action: str = Query(None, description="操作类型"),
    resource: str = Query(None, description="资源类型"),
    user_id: int = Query(None, description="操作人ID"),
    start_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """查询审计日志"""
    from datetime import datetime

    query = AuditLogSearchRequest(
        action=action,
        resource=resource,
        user_id=user_id,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        page=page,
        page_size=page_size,
    )
    return await compliance_service.search_logs(db, query)