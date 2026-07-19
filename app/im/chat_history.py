"""聊天历史 & 离线消息处理（成员C）"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.im import ImMessage


class ChatHistoryManager:
    """聊天历史管理器"""

    @staticmethod
    async def save_message(db: AsyncSession, message: ImMessage) -> ImMessage:
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_private_history(
        db: AsyncSession,
        user_id: int,
        other_user_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ImMessage], int]:
        condition = or_(
            and_(
                ImMessage.sender_id == user_id,
                ImMessage.receiver_id == other_user_id,
                ImMessage.chat_type == "private",
            ),
            and_(
                ImMessage.sender_id == other_user_id,
                ImMessage.receiver_id == user_id,
                ImMessage.chat_type == "private",
            ),
        )
        count_query = select(func.count(ImMessage.id)).where(condition, ImMessage.is_deleted == 0)
        total = await db.scalar(count_query) or 0
        query = (
            select(ImMessage)
            .where(condition, ImMessage.is_deleted == 0)
            .order_by(desc(ImMessage.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages, total

    @staticmethod
    async def get_group_history(
        db: AsyncSession,
        group_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ImMessage], int]:
        condition = and_(
            ImMessage.group_id == group_id,
            ImMessage.chat_type == "group",
            ImMessage.is_deleted == 0,
        )
        count_query = select(func.count(ImMessage.id)).where(condition)
        total = await db.scalar(count_query) or 0
        query = (
            select(ImMessage)
            .where(condition)
            .order_by(desc(ImMessage.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages, total

    @staticmethod
    async def get_offline_messages(
        db: AsyncSession,
        user_id: int,
        last_msg_id: Optional[int] = None,
        limit: int = 50,
    ) -> Tuple[List[ImMessage], bool]:
        condition = and_(
            ImMessage.is_deleted == 0,
            ImMessage.is_recalled == 0,
        )
        private_cond = and_(
            ImMessage.chat_type == "private",
            ImMessage.receiver_id == user_id,
        )
        if last_msg_id:
            private_cond = and_(private_cond, ImMessage.id > last_msg_id)
        query = (
            select(ImMessage)
            .where(and_(condition, private_cond))
            .order_by(ImMessage.id.asc())
            .limit(limit + 1)
        )
        result = await db.execute(query)
        messages = list(result.scalars().all())
        has_more = len(messages) > limit
        messages = messages[:limit]
        return messages, has_more

    @staticmethod
    async def mark_as_read(db: AsyncSession, message_id: int, user_id: int) -> bool:
        query = select(ImMessage).where(
            ImMessage.id == message_id,
            ImMessage.receiver_id == user_id,
            ImMessage.chat_type == "private",
            ImMessage.is_deleted == 0,
        )
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        if not message:
            return False
        message.is_read = 1
        message.read_at = datetime.utcnow()
        await db.flush()
        return True

    @staticmethod
    async def mark_private_messages_read(
        db: AsyncSession, user_id: int, other_user_id: int
    ) -> int:
        query = select(ImMessage).where(
            ImMessage.sender_id == other_user_id,
            ImMessage.receiver_id == user_id,
            ImMessage.chat_type == "private",
            ImMessage.is_read == 0,
            ImMessage.is_deleted == 0,
        )
        result = await db.execute(query)
        messages = list(result.scalars().all())
        now = datetime.utcnow()
        for msg in messages:
            msg.is_read = 1
            msg.read_at = now
        await db.flush()
        return len(messages)


chat_history_manager = ChatHistoryManager()