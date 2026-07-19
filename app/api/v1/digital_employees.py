"""F-06: 数字员工管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse, PageResult
from app.schemas.digital_employee import (
    ConversationItemResponse,
    DigitalEmployeeCreate,
    DigitalEmployeeListItem,
    DigitalEmployeeResponse,
    DigitalEmployeeUpdate,
    EmployeeSkillBindRequest,
    TestChatRequest,
    TestChatResponse,
)
from app.services.digital_employee_service import DigitalEmployeeService

router = APIRouter(prefix="/digital-employees", tags=["数字员工管理"])


@router.get("", response_model=ApiResponse)
async def list_employees(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取数字员工列表（分页+搜索）"""
    service = DigitalEmployeeService(db)
    employees, total = await service.get_employees(page=page, page_size=page_size, keyword=keyword)
    items = [DigitalEmployeeListItem.model_validate(e) for e in employees]
    return ApiResponse(data=PageResult(items=items, total=total, page=page, page_size=page_size))


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: DigitalEmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建数字员工"""
    service = DigitalEmployeeService(db)
    employee = await service.create_employee(data, created_by=current_user.id)
    return ApiResponse(code=201, message="数字员工创建成功", data=DigitalEmployeeResponse.model_validate(employee))


@router.get("/{employee_id}", response_model=ApiResponse)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取数字员工详情"""
    service = DigitalEmployeeService(db)
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    return ApiResponse(data=DigitalEmployeeResponse.model_validate(employee))


@router.put("/{employee_id}", response_model=ApiResponse)
async def update_employee(
    employee_id: int,
    data: DigitalEmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """修改数字员工"""
    service = DigitalEmployeeService(db)
    employee = await service.update_employee(employee_id, data)
    if not employee:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    return ApiResponse(message="数字员工更新成功", data=DigitalEmployeeResponse.model_validate(employee))


@router.delete("/{employee_id}", response_model=ApiResponse)
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除数字员工（软删除）"""
    service = DigitalEmployeeService(db)
    success = await service.delete_employee(employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    return ApiResponse(message="数字员工删除成功")


@router.put("/{employee_id}/status", response_model=ApiResponse)
async def toggle_employee_status(
    employee_id: int,
    is_enabled: bool = Query(..., description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """启用/禁用数字员工"""
    service = DigitalEmployeeService(db)
    employee = await service.toggle_status(employee_id, is_enabled)
    if not employee:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    return ApiResponse(message="状态更新成功", data=DigitalEmployeeResponse.model_validate(employee))


@router.put("/{employee_id}/skills", response_model=ApiResponse)
async def bind_skills(
    employee_id: int,
    data: EmployeeSkillBindRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """绑定技能到数字员工"""
    service = DigitalEmployeeService(db)
    try:
        employee = await service.bind_skills(employee_id, data.skill_ids)
        return ApiResponse(message="技能绑定成功", data=DigitalEmployeeResponse.model_validate(employee))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{employee_id}/skills", response_model=ApiResponse)
async def get_bound_skills(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取数字员工绑定的技能列表"""
    service = DigitalEmployeeService(db)
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    skills = await service.get_bound_skills(employee_id)
    return ApiResponse(data=skills)


@router.post("/{employee_id}/test-chat", response_model=ApiResponse)
async def test_chat(
    employee_id: int,
    data: TestChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """测试对话"""
    service = DigitalEmployeeService(db)
    try:
        result = await service.test_chat(employee_id, data.message)
        return ApiResponse(data=TestChatResponse(
            reply=result["reply"],
            model_id=result["model_id"],
            tokens_used=result.get("tokens_used"),
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.get("/{employee_id}/conversations", response_model=ApiResponse)
async def get_conversations(
    employee_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取数字员工对话记录"""
    service = DigitalEmployeeService(db)
    employee = await service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="数字员工不存在")
    convs, total = await service.get_conversations(employee_id, page=page, page_size=page_size)
    items = [ConversationItemResponse.model_validate(c) for c in convs]
    return ApiResponse(data=PageResult(items=items, total=total, page=page, page_size=page_size))
