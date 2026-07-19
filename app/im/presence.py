"""在线状态追踪（成员C）

使用 Redis 存储用户在线状态，支持多端登录。
"""

import time
from typing import Dict, List, Optional, Set

from loguru import logger

from app.core.redis import get_redis

PRESENCE_KEY = "im:presence"
GROUP_PRESENCE_KEY = "im:group:"


class PresenceTracker:
    """在线状态追踪器"""

    @staticmethod
    async def set_online(user_id: int, timeout: int = 300):
        redis = await get_redis()
        now = int(time.time())
        await redis.hset(PRESENCE_KEY, str(user_id), now)
        await redis.expire(PRESENCE_KEY, timeout)

    @staticmethod
    async def set_offline(user_id: int):
        redis = await get_redis()
        await redis.hdel(PRESENCE_KEY, str(user_id))

    @staticmethod
    async def is_online(user_id: int) -> bool:
        redis = await get_redis()
        return await redis.hexists(PRESENCE_KEY, str(user_id))

    @staticmethod
    async def get_last_online(user_id: int) -> Optional[int]:
        redis = await get_redis()
        val = await redis.hget(PRESENCE_KEY, str(user_id))
        return int(val) if val else None

    @staticmethod
    async def batch_is_online(user_ids: List[int]) -> Dict[int, bool]:
        if not user_ids:
            return {}
        redis = await get_redis()
        keys = [str(uid) for uid in user_ids]
        results = await redis.hmget(PRESENCE_KEY, keys)
        return {uid: bool(r) for uid, r in zip(user_ids, results)}

    @staticmethod
    async def get_all_online_users() -> Set[int]:
        redis = await get_redis()
        data = await redis.hgetall(PRESENCE_KEY)
        return {int(uid) for uid in data.keys()}

    @staticmethod
    async def get_online_count() -> int:
        redis = await get_redis()
        return await redis.hlen(PRESENCE_KEY)

    # ---- 群组在线 ----

    @staticmethod
    async def add_group_member(group_id: int, user_id: int):
        redis = await get_redis()
        key = f"{GROUP_PRESENCE_KEY}{group_id}:online"
        await redis.sadd(key, str(user_id))

    @staticmethod
    async def remove_group_member(group_id: int, user_id: int):
        redis = await get_redis()
        key = f"{GROUP_PRESENCE_KEY}{group_id}:online"
        await redis.srem(key, str(user_id))

    @staticmethod
    async def get_group_online_members(group_id: int) -> Set[int]:
        redis = await get_redis()
        key = f"{GROUP_PRESENCE_KEY}{group_id}:online"
        members = await redis.smembers(key)
        return {int(m) for m in members} if members else set()

    @staticmethod
    async def clear_group_members(group_id: int):
        redis = await get_redis()
        key = f"{GROUP_PRESENCE_KEY}{group_id}:online"
        await redis.delete(key)


presence_tracker = PresenceTracker()