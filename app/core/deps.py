"""FastAPI 公共依赖注入"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import SysUser

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> SysUser:
    """获取当前登录用户（返回 SysUser 对象）"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )

    user_id = int(payload.get("sub"))
    result = await db.execute(select(SysUser).where(SysUser.id == user_id, SysUser.is_deleted == 0))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被删除",
        )

    return user


async def require_role(roles: list[str]):
    """角色权限校验依赖工厂

    使用方式:
        @router.get("/admin/sensitive-words")
        async def list_words(
            current_user: SysUser = Depends(require_role(["admin", "super_admin"]))
        ):
            ...

    说明:
        - 通过角色的 code 字段匹配（如 "admin", "auditor", "super_admin"）
        - 匹配当前用户的任一角色即放行
        - SysUser.roles 为 UserRoleRel 列表，每个 UserRoleRel 有 role 属性（SysRole 对象）
    """
    async def _check_role(current_user: SysUser = Depends(get_current_user)):
        # 获取用户的所有角色
        user_role_codes = set()
        for rel in current_user.roles:
            if rel.role and not rel.role.is_deleted and rel.role.is_enabled:
                user_role_codes.add(rel.role.code)

        if not user_role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问（未分配任何角色）",
            )

        # 检查是否有任一角色在允许列表中
        if not any(role_code in user_role_codes for role_code in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {', '.join(roles)} 角色权限",
            )

        return current_user
    return _check_role
