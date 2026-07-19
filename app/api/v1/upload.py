"""文件上传接口（成员C）

提供文件上传功能，用于 IM 消息中的图片、文件等附件发送。
前端 FileUploader.vue 默认请求此接口上传文件。
"""

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from loguru import logger

from app.core.deps import get_current_user
from app.utils.response import success, error

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 上传目录
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    # 图片
    "jpg", "jpeg", "png", "gif", "bmp", "webp", "svg",
    # 文档
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv",
    # 音视频
    "mp3", "mp4", "wav", "avi", "mov",
    # 其他
    "zip", "rar", "7z",
}


def ensure_upload_dir():
    """确保上传目录存在"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # 按日期分子目录
    date_dir = datetime.now().strftime("%Y/%m/%d")
    full_path = os.path.join(UPLOAD_DIR, date_dir)
    os.makedirs(full_path, exist_ok=True)
    return full_path


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    # current_user: dict = Depends(get_current_user),  # TODO: 等成员A JWT就绪后启用
):
    """上传文件
    
    返回上传后的文件访问 URL。
    前端预期: response.data.url 为文件访问地址。
    """
    # 1. 校验文件扩展名
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return error(code=400, msg=f"不支持的文件类型: .{ext}")

    # 2. 校验文件大小（读取前先检查 Content-Length）
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return error(code=400, msg=f"文件大小不能超过 10MB")

    # 3. 生成唯一文件名保存
    date_path = ensure_upload_dir()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(date_path, unique_name)

    try:
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"文件保存失败: {e}")
        return error(code=500, msg="文件保存失败")

    # 4. 返回文件访问 URL
    # 前端通过 /uploads/ 路径访问静态文件
    file_url = f"/uploads/{datetime.now().strftime('%Y/%m/%d')}/{unique_name}"
    logger.info(f"文件上传成功: {filename} -> {file_url} (大小: {len(content)} bytes)")

    return success(data={"url": file_url})