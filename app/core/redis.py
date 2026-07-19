"""Redis 连接池管理

提供全局 Redis 客户端，所有 Redis 操作通过 get_redis() 获取实例。

使用示例:
    from app.core.redis import get_redis
    redis = await get_redis()
    await redis.set("key", "value")
"""

from typing import Optional

from redis.asyncio import BlockingConnectionPool, Redis
from loguru import logger

from app.config import settings

_pool: Optional[BlockingConnectionPool] = None
_redis: Optional[Redis] = None


async def init_redis() -> None:
    """初始化 Redis 连接池，在应用启动时调用一次。"""
    global _pool, _redis

    if _redis is not None:
        logger.warning("Redis 已经初始化，跳过重复初始化")
        return

    logger.info("正在连接 Redis: {}", settings.REDIS_URL)
    _pool = BlockingConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        timeout=10,
        decode_responses=True,
    )
    _redis = Redis(connection_pool=_pool)
    await _redis.ping()
    logger.success("Redis 连接成功")


async def close_redis() -> None:
    """关闭 Redis 连接池，在应用关闭时调用。"""
    global _pool, _redis

    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Redis 客户端已关闭")
    if _pool is not None:
        await _pool.aclose()
        _pool = None
        logger.info("Redis 连接池已关闭")


async def get_redis() -> Redis:
    """获取 Redis 客户端实例。

    首次调用时自动初始化连接池。之后每次调用返回同一个全局实例。
    """
    global _redis
    if _redis is None:
        await init_redis()
    return _redis
