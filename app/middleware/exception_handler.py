"""全局异常处理中间件

捕获未处理的异常，统一返回 JSON 错误响应。
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    logger.error(f"未处理的异常 [{request.method} {request.url.path}]: {exc}")

    # 根据异常类型返回不同错误码
    status_code = 500
    error_code = 50000
    message = "服务器内部错误"

    if isinstance(exc, ValueError):
        status_code = 400
        error_code = 40200
        message = str(exc)
    elif isinstance(exc, PermissionError):
        status_code = 403
        error_code = 40100
        message = "无权限访问"

    return JSONResponse(
        status_code=status_code,
        content={"code": error_code, "message": message, "data": None},
    )
