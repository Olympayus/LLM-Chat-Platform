"""File management API (F-FL) — Member F"""

from fastapi import APIRouter, Depends, File, Query, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.file_record import FileResponse, FileShareCreate, FileShareResponse
from app.services.file_service import FileService
from app.utils.response import success, error, paginate

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Upload a file"""
    content = await file.read()
    if len(content) > FileService.MAX_FILE_SIZE:
        return error(code=400, msg=f"File exceeds {FileService.MAX_FILE_SIZE // 1024 // 1024}MB limit")
    service = FileService(db)
    record = await service.save_file(file.filename or "unknown", content, file.content_type or "application/octet-stream", current_user.id)
    return success(data={"file_id": record.id, "url": f"/uploads/{record.file_path}"})


@router.get("")
async def list_files(
    category: str = Query(None), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user),
):
    """List user files"""
    service = FileService(db)
    items, total = await service.get_files(current_user.id, category, page, page_size)
    return paginate(items=[FileResponse.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.get("/{file_id}")
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """Get file detail"""
    service = FileService(db)
    record = await service.get_file(file_id)
    if not record: return error(code=404, msg="File not found")
    return success(data=FileResponse.model_validate(record))


@router.delete("/{file_id}")
async def delete_file(
    file_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user),
):
    """Soft delete file"""
    service = FileService(db)
    ok = await service.delete_file(file_id)
    if not ok: return error(code=404, msg="File not found")
    return success(message="File deleted")


@router.post("/{file_id}/share")
async def share_file(
    file_id: int, data: FileShareCreate = FileShareCreate(),
    db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user),
):
    """Create share link"""
    service = FileService(db)
    share = await service.create_share(file_id, current_user.id, data.password, data.expire_days)
    if not share: return error(code=404, msg="File not found")
    return success(data=FileShareResponse.model_validate(share))
