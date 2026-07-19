"""WebSocket 连接管理器（成员C）

管理所有 WebSocket 连接，支持多端登录、心跳保活、消息推送。

集成点（与成员D配合）:
- broadcast_recall(): 供 compliance_service.recall_message() 调用
- send_group(): 供 compliance_service.send_system_message() 调用
"""

import asyncio
from typing import Dict, List, Optional, Set

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # user_id -> list[WebSocket] 多端登录支持
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # websocket -> user_id 反向映射
        self._ws_to_user: Dict[int, int] = {}
        # group_id -> set[user_id] 群在线成员
        self.group_members: Dict[int, Set[int]] = {}
        # user_id -> set[group_id] 用户加入的群
        self.user_groups: Dict[int, Set[int]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int):
        """建立连接"""
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            self._ws_to_user[id(websocket)] = user_id
        logger.info(f"🟢 用户 {user_id} 已连接")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """断开连接"""
        async with self._lock:
            if user_id in self.active_connections:
                try:
                    self.active_connections[user_id].remove(websocket)
                except ValueError:
                    pass
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    if user_id in self.user_groups:
                        for gid in self.user_groups[user_id]:
                            if gid in self.group_members:
                                self.group_members[gid].discard(user_id)
                        del self.user_groups[user_id]
            self._ws_to_user.pop(id(websocket), None)
        logger.info(f"🔴 用户 {user_id} 已断开")

    async def send_personal(self, user_id: int, message: dict):
        """向用户的所有连接推送消息"""
        connections = self.active_connections.get(user_id, [])
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"发送消息给用户 {user_id} 失败: {e}")

    async def send_group(self, group_id: int, message: dict, exclude_user_id: Optional[int] = None):
        """向群组所有在线成员广播消息（成员D 的 send_system_message 调用此接口）"""
        member_ids = self.group_members.get(group_id, set()).copy()
        for uid in member_ids:
            if exclude_user_id and uid == exclude_user_id:
                continue
            await self.send_personal(uid, message)

    async def broadcast_recall(self, group_id: Optional[int], message_id: int, reason: str):
        """广播撤回事件（成员D 的 recall_message 调用此接口）
        
        Args:
            group_id: 群组ID（为 None 表示私聊撤回）
            message_id: 被撤回的消息ID
            reason: 撤回原因
        """
        recall_data = {
            "type": "message_recall",
            "data": {
                "message_id": message_id,
                "reason": reason,
            },
        }
        if group_id:
            # 群聊：广播给群组所有在线成员
            await self.send_group(group_id, recall_data)
        else:
            # 私聊：广播给所有在线用户（简化处理）
            user_ids = list(self.active_connections.keys())
            for uid in user_ids:
                await self.send_personal(uid, recall_data)

    async def broadcast_system(self, message: dict):
        """向所有在线用户广播系统消息"""
        user_ids = list(self.active_connections.keys())
        for uid in user_ids:
            await self.send_personal(uid, message)

    async def join_group(self, user_id: int, group_id: int):
        """用户加入群组在线列表"""
        async with self._lock:
            if group_id not in self.group_members:
                self.group_members[group_id] = set()
            self.group_members[group_id].add(user_id)
            if user_id not in self.user_groups:
                self.user_groups[user_id] = set()
            self.user_groups[user_id].add(group_id)

    async def leave_group(self, user_id: int, group_id: int):
        """用户离开群组在线列表"""
        async with self._lock:
            if group_id in self.group_members:
                self.group_members[group_id].discard(user_id)
            if user_id in self.user_groups:
                self.user_groups[user_id].discard(group_id)

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections and bool(self.active_connections[user_id])

    def get_online_count(self) -> int:
        return len(self.active_connections)

    def get_online_users(self) -> List[int]:
        return list(self.active_connections.keys())

    def get_group_online_members(self, group_id: int) -> Set[int]:
        return self.group_members.get(group_id, set()).copy()

    def get_user_id_by_ws(self, websocket: WebSocket) -> Optional[int]:
        return self._ws_to_user.get(id(websocket))


# 全局单例（成员D 通过此实例调用 broadcast_recall / send_group）
connection_manager = ConnectionManager()