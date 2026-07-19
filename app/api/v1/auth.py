"""认证与用户管理 API 路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.schemas.auth import (
    # 认证
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    ChangePasswordRequest,
    # 用户
    UserCreate, UserUpdate, UserPasswordReset, AdminPasswordReset,
    UserResponse, UserListResponse, UserRoleAssign,
    # 部门
    DeptCreate, DeptUpdate, DeptResponse,
    # 角色
    RoleCreate, RoleUpdate, RoleMenuAssign, RoleResponse,
    # 菜单
    MenuCreate, MenuUpdate, MenuResponse,
)
from app.services.auth_service import (
    AuthService, UserService, DeptService, RoleService, MenuService,
    AuthError, BusinessError, NotFoundError,
)
from app.models.user import SysUser
from app.core.database import get_db
from app.utils.response import success, error

router = APIRouter()


# ==================== 认证接口 ====================

@router.post("/auth/login", response_model=LoginResponse, summary="用户登录")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    try:
        user, token = await AuthService.authenticate(db, data.username, data.password)
        return success(data={
            "token": token,
            "user": UserResponse.model_validate(user).model_dump()
        })
    except (AuthError, BusinessError) as e:
        return error(code=401, message=str(e))


@router.post("/auth/register", response_model=RegisterResponse, summary="用户注册")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    try:
        user = await AuthService.register(db, data.model_dump())
        return success(data={
            "user": UserResponse.model_validate(user).model_dump()
        })
    except BusinessError as e:
        return error(code=400, message=str(e))


@router.post("/auth/logout", summary="用户登出")
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """用户登出"""
    try:
        await AuthService.logout(db, current_user.id)
        return success(message="登出成功")
    except Exception as e:
        return error(message=str(e))


@router.put("/auth/change-password", summary="修改密码")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """修改当前用户密码"""
    try:
        await AuthService.change_password(db, current_user.id, data)
        return success(message="密码修改成功")
    except (AuthError, BusinessError) as e:
        return error(code=400, message=str(e))


@router.post("/auth/refresh", summary="刷新 Token")
async def refresh_token(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """刷新 Token"""
    try:
        access_token, refresh_token = await AuthService.refresh_token(db, current_user.id)
        return success(data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1440
        })
    except AuthError as e:
        return error(code=401, message=str(e))


@router.get("/auth/me", summary="获取当前用户信息")
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前登录用户信息"""
    try:
        return success(data={
            "user": UserResponse.model_validate(current_user).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


# ==================== 用户管理接口 ====================

@router.post("/users", summary="创建用户")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建用户（管理员）"""
    try:
        user = await UserService.create_user(db, data)
        return success(data={
            "user": UserResponse.model_validate(user).model_dump()
        })
    except BusinessError as e:
        return error(code=400, message=str(e))


@router.put("/users/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新用户信息"""
    try:
        user = await UserService.update_user(db, user_id, data)
        return success(data={
            "user": UserResponse.model_validate(user).model_dump()
        })
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """删除用户（软删除）"""
    try:
        await UserService.delete_user(db, user_id)
        return success(message="删除成功")
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.put("/users/{user_id}/admin-reset-password", summary="管理员重置密码")
async def admin_reset_password(
    user_id: int,
    data: AdminPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """管理员重置用户密码"""
    try:
        await UserService.admin_reset_password(db, user_id, data)
        return success(message="密码重置成功")
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.post("/users/{user_id}/reset-password", summary="重置密码")
async def reset_password(
    user_id: int,
    data: UserPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """重置密码"""
    try:
        await UserService.reset_password(db, user_id, data)
        return success(message="密码重置成功")
    except (NotFoundError, BusinessError) as e:
        return error(code=400, message=str(e))


@router.get("/users", summary="用户列表")
async def list_users(
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    dept_id: Optional[int] = Query(None, description="部门ID"),
    status: Optional[int] = Query(None, description="状态"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """用户列表（分页）"""
    try:
        users, total = await UserService.list_users(
            db, keyword=keyword, dept_id=dept_id,
            status=status, page=page, page_size=page_size
        )
        return success(data={
            "items": [UserResponse.model_validate(u).model_dump() for u in users],
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/users/{user_id}", summary="获取用户详情")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取用户详情"""
    try:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return error(code=404, message="用户不存在")
        return success(data={
            "user": UserResponse.model_validate(user).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


@router.post("/users/{user_id}/roles", summary="分配用户角色")
async def assign_user_roles(
    user_id: int,
    data: UserRoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """分配用户角色"""
    try:
        await UserService.assign_roles(db, user_id, data)
        return success(message="角色分配成功")
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.get("/users/{user_id}/roles", summary="获取用户角色")
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取用户角色列表"""
    try:
        roles = await UserService.get_user_roles(db, user_id)
        return success(data={
            "roles": [RoleResponse.model_validate(r).model_dump() for r in roles]
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/users/{user_id}/permissions", summary="获取用户权限")
async def get_user_permissions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取用户权限标识列表"""
    try:
        permissions = await UserService.get_user_permissions(db, user_id)
        return success(data={"permissions": permissions})
    except Exception as e:
        return error(message=str(e))


# ==================== 部门管理接口 ====================

@router.post("/depts", summary="创建部门")
async def create_dept(
    data: DeptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建部门"""
    try:
        dept = await DeptService.create_dept(db, data)
        return success(data={
            "dept": DeptResponse.model_validate(dept).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


@router.put("/depts/{dept_id}", summary="更新部门")
async def update_dept(
    dept_id: int,
    data: DeptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新部门"""
    try:
        dept = await DeptService.update_dept(db, dept_id, data)
        return success(data={
            "dept": DeptResponse.model_validate(dept).model_dump()
        })
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.delete("/depts/{dept_id}", summary="删除部门")
async def delete_dept(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """删除部门"""
    try:
        await DeptService.delete_dept(db, dept_id)
        return success(message="删除成功")
    except (NotFoundError, BusinessError) as e:
        return error(code=400, message=str(e))


@router.get("/depts/tree", summary="获取部门树")
async def get_dept_tree(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取部门树"""
    try:
        depts = await DeptService.get_dept_tree(db)
        return success(data={
            "depts": [DeptResponse.model_validate(d).model_dump() for d in depts]
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/depts/{dept_id}", summary="获取部门详情")
async def get_dept(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取部门详情"""
    try:
        dept = await DeptService.get_dept_by_id(db, dept_id)
        if not dept:
            return error(code=404, message="部门不存在")
        return success(data={
            "dept": DeptResponse.model_validate(dept).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


# ==================== 角色管理接口 ====================

@router.post("/roles", summary="创建角色")
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建角色"""
    try:
        role = await RoleService.create_role(db, data)
        return success(data={
            "role": RoleResponse.model_validate(role).model_dump()
        })
    except BusinessError as e:
        return error(code=400, message=str(e))


@router.put("/roles/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新角色"""
    try:
        role = await RoleService.update_role(db, role_id, data)
        return success(data={
            "role": RoleResponse.model_validate(role).model_dump()
        })
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """删除角色"""
    try:
        await RoleService.delete_role(db, role_id)
        return success(message="删除成功")
    except (NotFoundError, BusinessError) as e:
        return error(code=400, message=str(e))


@router.get("/roles", summary="角色列表")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """角色列表"""
    try:
        roles = await RoleService.list_roles(db)
        return success(data={
            "roles": [RoleResponse.model_validate(r).model_dump() for r in roles]
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/roles/{role_id}", summary="获取角色详情")
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取角色详情"""
    try:
        role = await RoleService.get_role_by_id(db, role_id)
        if not role:
            return error(code=404, message="角色不存在")
        return success(data={
            "role": RoleResponse.model_validate(role).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


@router.post("/roles/{role_id}/menus", summary="分配角色菜单")
async def assign_role_menus(
    role_id: int,
    data: RoleMenuAssign,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """分配角色菜单权限"""
    try:
        await RoleService.assign_menus(db, role_id, data)
        return success(message="菜单分配成功")
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.get("/roles/{role_id}/menus", summary="获取角色菜单")
async def get_role_menus(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取角色的菜单列表"""
    try:
        menus = await RoleService.get_role_menus(db, role_id)
        return success(data={
            "menus": [MenuResponse.model_validate(m).model_dump() for m in menus]
        })
    except Exception as e:
        return error(message=str(e))


# ==================== 菜单管理接口 ====================

@router.post("/menus", summary="创建菜单")
async def create_menu(
    data: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建菜单"""
    try:
        menu = await MenuService.create_menu(db, data)
        return success(data={
            "menu": MenuResponse.model_validate(menu).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


@router.put("/menus/{menu_id}", summary="更新菜单")
async def update_menu(
    menu_id: int,
    data: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新菜单"""
    try:
        menu = await MenuService.update_menu(db, menu_id, data)
        return success(data={
            "menu": MenuResponse.model_validate(menu).model_dump()
        })
    except NotFoundError as e:
        return error(code=404, message=str(e))


@router.delete("/menus/{menu_id}", summary="删除菜单")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """删除菜单"""
    try:
        await MenuService.delete_menu(db, menu_id)
        return success(message="删除成功")
    except (NotFoundError, BusinessError) as e:
        return error(code=400, message=str(e))


@router.get("/menus/tree", summary="获取菜单树")
async def get_menu_tree(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取菜单树"""
    try:
        menus = await MenuService.get_menu_tree(db)
        return success(data={
            "menus": [MenuResponse.model_validate(m).model_dump() for m in menus]
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/menus/{menu_id}", summary="获取菜单详情")
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取菜单详情"""
    try:
        menu = await MenuService.get_menu_by_id(db, menu_id)
        if not menu:
            return error(code=404, message="菜单不存在")
        return success(data={
            "menu": MenuResponse.model_validate(menu).model_dump()
        })
    except Exception as e:
        return error(message=str(e))


@router.get("/menus/user/tree", summary="获取用户菜单树")
async def get_user_menu_tree(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前用户可见的菜单树"""
    try:
        menus = await MenuService.get_user_menus(db, current_user.id)
        return success(data={
            "menus": [MenuResponse.model_validate(m).model_dump() for m in menus]
        })
    except Exception as e:
        return error(message=str(e))