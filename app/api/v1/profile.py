"""个人中心 API 路由 - F-PF 个人中心 (v3 新增)"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import SysUser
from app.models.login_history import LoginHistory
from app.utils.response import success, error
from app.services.auth_service import AuthService
from sqlalchemy import select, desc

router = APIRouter()

# [F-PF] 头像上传路径，由成员F配置 upload 端点后接入
# TODO(成员A): 接入 upload API 后实现头像上传


@router.get("/profile", summary="获取个人资料")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前登录用户的个人资料"""
    try:
        user = await AuthService.get_current_user(db, current_user.id)
        return success(data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "mobile": user.mobile,
            "real_name": user.real_name,
            "avatar_url": user.avatar_url,
            "dept_id": user.dept_id,
            "status": user.status,
            "is_online": user.is_online,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "last_login_ip": user.last_login_ip,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    except Exception as e:
        return error(message=str(e))


@router.put("/profile", summary="更新个人资料")
async def update_profile(
    email: Optional[str] = None,
    mobile: Optional[str] = None,
    real_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新当前登录用户的个人资料"""
    try:
        if email is not None:
            current_user.email = email
        if mobile is not None:
            current_user.mobile = mobile
        if real_name is not None:
            current_user.real_name = real_name

        await db.commit()
        await db.refresh(current_user)
        return success(data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "mobile": current_user.mobile,
            "real_name": current_user.real_name,
            "avatar_url": current_user.avatar_url,
        })
    except Exception as e:
        return error(message=str(e))


@router.post("/profile/avatar", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """上传用户头像"""
    try:
        # TODO(成员A): 接入 upload API 后将文件保存到对象存储，更新 avatar_url
        # 当前占位：直接更新 avatar_url 为空字符串，待成员F提供 upload 接口后完善
        # 预期: avatar_url = await upload_service.upload(file, folder="avatars")
        return error(code=501, message="头像上传功能待接入 upload API，请联系成员F")
    except Exception as e:
        return error(message=str(e))


@router.get("/profile/login-history", summary="获取登录历史")
async def get_login_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前用户的登录历史记录"""
    try:
        # 查询总数
        count_result = await db.execute(
            select(LoginHistory.id).where(LoginHistory.user_id == current_user.id)
        )
        total = len(count_result.all())

        # 分页查询
        result = await db.execute(
            select(LoginHistory)
            .where(LoginHistory.user_id == current_user.id)
            .order_by(desc(LoginHistory.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        records = result.scalars().all()

        items = []
        for r in records:
            items.append({
                "id": r.id,
                "login_ip": r.login_ip,
                "user_agent": r.user_agent,
                "login_status": r.login_status,
                "fail_reason": r.fail_reason,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        return success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        })
    except Exception as e:
        return error(message=str(e))