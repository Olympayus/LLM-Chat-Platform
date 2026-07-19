"""Crawler management REST API."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import SysUser
from app.schemas.crawler import (
    CrawlerExecutionLogQuery,
    CrawlerTaskCreate,
    CrawlerTaskUpdate,
    CrawlerTestRequest,
    DataCleanRuleCreate,
    DataCleanRuleUpdate,
)
from app.services.crawler_service import crawler_service
from app.utils.response import error, paginate, success

router = APIRouter(prefix="/crawlers", tags=["Crawler"])


@router.post("", summary="Create task")
async def create_task(
    body: CrawlerTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.create_task(db, body, created_by=current_user.id)
    return success(data=result.model_dump())


@router.get("", summary="List tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.list_tasks(
        db, page=page, page_size=page_size, keyword=keyword
    )
    return paginate(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{task_id}", summary="Get task")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.get_task(db, task_id)
    if result is None:
        return error(code=404, msg=f"Task {task_id} not found")
    return success(data=result.model_dump())


@router.put("/{task_id}", summary="Update task")
async def update_task(
    task_id: int,
    body: CrawlerTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.update_task(db, task_id, body)
    if result is None:
        return error(code=404, msg=f"Task {task_id} not found")
    return success(data=result.model_dump())


@router.delete("/{task_id}", summary="Delete task")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    ok = await crawler_service.delete_task(db, task_id)
    if not ok:
        return error(code=404, msg=f"Task {task_id} not found")
    return success(message="Deleted")


@router.post("/{task_id}/run", summary="Run task")
async def run_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.execute_task(task_id, db)
    if result.status == "failed":
        return error(code=500, msg=result.error_message or "Execution failed", data=result.model_dump())
    return success(data=result.model_dump())


@router.post("/test-parse", summary="Test parse rules")
async def test_parse(
    body: CrawlerTestRequest,
):
    result = await crawler_service.test_parse(body)
    return success(data=result.model_dump())


@router.get("/{task_id}/logs", summary="Task logs")
async def get_task_logs(
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = CrawlerExecutionLogQuery(
        task_id=task_id, status=status, page=page, page_size=page_size,
    )
    result = await crawler_service.get_logs(db, query)
    return paginate(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.post("/clean-rules", summary="Create clean rule")
async def create_clean_rule(
    body: DataCleanRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.create_clean_rule(db, body)
    return success(data=result.model_dump())


@router.get("/clean-rules", summary="List clean rules")
async def list_clean_rules(
    task_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.list_clean_rules(
        db, task_id=task_id, page=page, page_size=page_size
    )
    return paginate(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/clean-rules/{rule_id}", summary="Get clean rule")
async def get_clean_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.get_clean_rule(db, rule_id)
    if result is None:
        return error(code=404, msg=f"Rule {rule_id} not found")
    return success(data=result.model_dump())


@router.put("/clean-rules/{rule_id}", summary="Update clean rule")
async def update_clean_rule(
    rule_id: int,
    body: DataCleanRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    result = await crawler_service.update_clean_rule(db, rule_id, body)
    if result is None:
        return error(code=404, msg=f"Rule {rule_id} not found")
    return success(data=result.model_dump())


@router.delete("/clean-rules/{rule_id}", summary="Delete clean rule")
async def delete_clean_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    ok = await crawler_service.delete_clean_rule(db, rule_id)
    if not ok:
        return error(code=404, msg=f"Rule {rule_id} not found")
    return success(message="Deleted")
