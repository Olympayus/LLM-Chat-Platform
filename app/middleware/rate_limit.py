"""API 限流中间件

使用 Redis 滑动窗口实现：
- 全局限流：每个用户每分钟 60 次
- 登录接口：每个 IP 每分钟 10 次
- 注册接口：每个 IP 每分钟 3 次
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.redis import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis 滑动窗口限流中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 仅对 /api/v1/ 路径限流
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)

        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"

        # 根据路径选择限流策略
        if "/auth/login" in request.url.path or "/auth/refresh" in request.url.path:
            limit = 10  # 登录接口
        elif "/auth/register" in request.url.path:
            limit = 3   # 注册接口
        elif "/auth/forgot-password" in request.url.path:
            limit = 1   # 密码重置（防刷邮件）
        else:
            limit = 60  # 全局限流

        window = 60  # 滑动窗口 60 秒

        try:
            redis = await get_redis()
            key = f"rate_limit:{client_ip}:{request.url.path}"
            now = time.time()
            window_start = now - window

            # 滑动窗口：移除过期记录 + 计数
            await redis.zremrangebyscore(key, 0, window_start)
            count = await redis.zcard(key)

            if count >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "code": 40401,
                        "message": f"操作频率过快，请稍后再试（{window}秒内最多{limit}次）",
                        "data": None,
                    },
                )

            # 记录本次请求
            await redis.zadd(key, {str(now): now})
            await redis.expire(key, window + 10)

        except Exception:
            # Redis 不可用时，放行请求（不阻塞）
            pass

        return await call_next(request)
