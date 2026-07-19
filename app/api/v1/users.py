"""用户组织管理 API 路由 - F-01 用户组织管理

说明：用户/部门/角色/菜单的增删改查接口已在 auth.py 中实现。
本文件重新导出 auth_router 以保持模块结构清晰。
"""

from app.api.v1.auth import router

__all__ = ["router"]