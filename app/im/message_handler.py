"""消息路由器（成员C）

负责 WebSocket 消息的接收、验证、持久化、分发。

集成点（与成员D配合）:
- 敏感词检测: compliance_service 已在 API 层预留调用点
- ES 同步: elasticsearch_service 已在 API 层预留调用点
- 撤回联动: compliance_service.recall_message() 调用 connection_manager.broadcast_recall()
"""

import json
import time
from datetime import datetime
from typing import Optional

from loguru import logger

from app.core.database import async_session_factory
from app.models.im import ImMessage
from app.im.connection_manager import connection_manager
from app.im.chat_history import chat_history_manager
from app.utils.sensitive_filter import sensitive_filter
from app.services.elasticsearch_service import es_service


class MessageHandler:
    """消息处理器"""

    @staticmethod
    async def generate_message_id() -> int:
        """生成雪花算法风格的消息ID"""
        now = int(time.time() * 1000)
        rand = int.from_bytes(__import__("os").urandom(3), "big") % 10000
        return (now << 16) | rand

    @staticmethod
    async def handle_message(
        sender_id: int,
        chat_type: str,
        receiver_id: Optional[int],
        group_id: Optional[int],
        msg_type: str,
        content: str,
        extra: Optional[dict] = None,
        client_msg_id: Optional[str] = None,
    ) -> dict:
        """处理接收到的消息
        
        消息流程:
        1. 创建消息记录
        2. 持久化到 MySQL
        3. 通过 WebSocket 分发
        4. 返回 ACK

        已集成:
        - sensitive_filter.check() 敏感词检测 ✅
        - elasticsearch_service.index_message() ES 索引同步 ✅
        """
        # 0. 敏感词检测（成员D 的合规模块）
        has_block, has_audit, matched_words = sensitive_filter.check(content)
        if has_block:
            logger.warning(f"⛔ 用户 {sender_id} 的消息含违规内容，已拦截: {matched_words}")
            return {
                "type": "error",
                "data": {"message": "消息包含违规内容，已被系统拦截", "matched_words": matched_words, "client_msg_id": client_msg_id},
            }
        need_audit = True if has_audit else False
        if need_audit:
            logger.info(f"📝 用户 {sender_id} 的消息含需审计内容: {matched_words}")

        # 0.5 禁言检测（成员D 的合规禁言）
        try:
            from app.core.redis import get_redis
            redis = await get_redis()
            is_muted = await redis.exists(f"mute:{sender_id}")
            if is_muted:
                logger.warning(f"🔇 用户 {sender_id} 已被禁言，消息被拦截")
                return {
                    "type": "error",
                    "data": {"message": "您已被禁言，无法发送消息", "client_msg_id": client_msg_id},
                }
        except Exception:
            pass  # Redis 不可用时不阻塞消息

        # 1. 创建消息记录
        msg_id = await MessageHandler.generate_message_id()
        message = ImMessage(
            id=msg_id,
            chat_type=chat_type,
            sender_type="user",
            sender_id=sender_id,
            receiver_id=receiver_id,
            group_id=group_id,
            msg_type=msg_type,
            content=content,
            extra=extra or {},
            need_audit=1 if need_audit else 0,
        )

        # 2. 持久化到 MySQL
        try:
            async with async_session_factory() as db:
                await chat_history_manager.save_message(db, message)
                await db.commit()
                await db.refresh(message)
        except Exception as e:
            logger.error(f"❌ 消息持久化失败: {e}")
            return {
                "type": "error",
                "data": {"message": "消息发送失败", "client_msg_id": client_msg_id},
            }

        # 3. 构造推送消息
        push_data = {
            "id": msg_id,
            "chat_type": chat_type,
            "sender_type": "user",
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "group_id": group_id,
            "msg_type": msg_type,
            "content": content,
            "extra": extra,
            "is_recalled": 0,
            "is_read": 0,
            "need_audit": 1 if need_audit else 0,
            "created_at": message.created_at.isoformat() if message.created_at else datetime.utcnow().isoformat(),
        }

        ws_message = {
            "type": "message",
            "data": push_data,
            "server_time": int(time.time() * 1000),
        }

        # 4. 分发消息
        if chat_type == "private" and receiver_id:
            await connection_manager.send_personal(receiver_id, ws_message)
            await connection_manager.send_personal(sender_id, ws_message)
        elif chat_type == "group" and group_id:
            await connection_manager.send_group(
                group_id, ws_message, exclude_user_id=sender_id
            )
            await connection_manager.send_personal(sender_id, ws_message)

        # 5. 异步索引到 ES（不影响主流程）
        try:
            es_doc = {
                "message_id": msg_id,
                "chat_type": chat_type,
                "sender_type": "user",
                "sender_id": sender_id,
                "group_id": group_id or 0,
                "content": content,
                "msg_type": msg_type,
                "is_recalled": False,
                "created_at": message.created_at.isoformat() if message.created_at else datetime.utcnow().isoformat(),
            }
            await es_service.index_message(es_doc)
        except Exception as e:
            logger.warning(f"ES 索引同步失败（不影响消息发送）: {e}")

        # 6. 返回 ACK
        return {
            "type": "ack",
            "data": {
                "client_msg_id": client_msg_id,
                "message_id": msg_id,
                "server_time": int(time.time() * 1000),
            },
        }

    @staticmethod
    async def handle_recall(message_id: int, user_id: int, reason: Optional[str] = None) -> dict:
        """处理用户自助撤回消息"""
        async with async_session_factory() as db:
            from sqlalchemy import select

            query = (
                select(ImMessage)
                .where(
                    ImMessage.id == message_id,
                    ImMessage.sender_id == user_id,
                    ImMessage.is_deleted == 0,
                )
            )
            result = await db.execute(query)
            message = result.scalar_one_or_none()

            if not message:
                return {"type": "error", "data": {"message": "消息不存在或无权撤回"}}

            if message.created_at:
                elapsed = (datetime.utcnow() - message.created_at).total_seconds()
                if elapsed > 300:
                    return {"type": "error", "data": {"message": "消息发送已超过5分钟，无法撤回"}}

            message.is_recalled = 1
            message.recall_reason = reason or "用户撤回"
            message.recalled_by = user_id
            await db.commit()

        # 广播撤回通知
        recall_data = {
            "type": "message_recall",
            "data": {
                "message_id": message_id,
                "chat_type": message.chat_type if message else "private",
                "group_id": message.group_id if message else None,
                "reason": reason or "用户撤回",
            },
        }

        if message and message.chat_type == "group" and message.group_id:
            await connection_manager.send_group(message.group_id, recall_data)
        elif message and message.receiver_id:
            await connection_manager.send_personal(message.receiver_id, recall_data)

        await connection_manager.send_personal(user_id, recall_data)

        # 同步从 ES 删除（不影响主流程）
        try:
            await es_service.delete_by_message_id(message_id)
        except Exception as e:
            logger.warning(f"ES 删除索引失败（不影响撤回）: {e}")

        return recall_data

    @staticmethod
    async def handle_ping() -> dict:
        return {"type": "pong", "server_time": int(time.time() * 1000)}


message_handler = MessageHandler()