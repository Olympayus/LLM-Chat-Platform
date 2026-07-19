"""WebSocket 端点（成员C）

IM 实时通信 WebSocket 接口。
"""

import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from loguru import logger

from app.core.security import decode_access_token
from app.im.connection_manager import connection_manager
from app.im.message_handler import message_handler
from app.im.presence import presence_tracker

router = APIRouter()


@router.websocket("/ws/im")
async def websocket_im(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Token"),
):
    """IM WebSocket 端点
    
    连接: ws://host:port/api/v1/ws/im?token={jwt}
    
    消息协议:
    发送消息: {"type": "message", "data": {"chat_type":"private|group", "receiver_id":123, "group_id":456, "msg_type":"text", "content":"hello"}, "client_msg_id": "uuid"}
    心跳:     {"type": "ping"}
    撤回:     {"type": "recall", "message_id": 12345}
    加入群:   {"type": "join_group", "group_id": 456}
    离开群:   {"type": "leave_group", "group_id": 456}
    """
    # 1. JWT 认证
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Token 无效或已过期")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=4001, reason="Token 中缺少用户信息")
        return

    # 2. 接受 WebSocket 连接
    await websocket.accept()
    await connection_manager.connect(websocket, user_id)
    await presence_tracker.set_online(int(user_id))

    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "消息格式错误，请发送 JSON"},
                })
                continue

            msg_type = data.get("type", "message")
            client_msg_id = data.get("client_msg_id")

            if msg_type == "ping":
                response = await message_handler.handle_ping()
                await websocket.send_json(response)

            elif msg_type == "message":
                msg_data = data.get("data", {})
                try:
                    response = await message_handler.handle_message(
                        sender_id=user_id,
                        chat_type=msg_data.get("chat_type", "private"),
                        receiver_id=msg_data.get("receiver_id"),
                        group_id=msg_data.get("group_id"),
                        msg_type=msg_data.get("msg_type", "text"),
                        content=msg_data.get("content", ""),
                        extra=msg_data.get("extra"),
                        client_msg_id=client_msg_id,
                    )
                    await websocket.send_json(response)
                except Exception as e:
                    logger.warning(f"消息处理失败: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": f"消息处理失败: {str(e)}", "client_msg_id": client_msg_id},
                    })

            elif msg_type == "recall":
                message_id = data.get("message_id")
                if not message_id:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "缺少 message_id"},
                    })
                    continue
                reason = data.get("reason")
                response = await message_handler.handle_recall(
                    message_id=message_id, user_id=user_id, reason=reason,
                )
                if response.get("type") == "error":
                    await websocket.send_json(response)

            elif msg_type == "join_group":
                group_id = data.get("group_id")
                if group_id:
                    await connection_manager.join_group(user_id, group_id)

            elif msg_type == "leave_group":
                group_id = data.get("group_id")
                if group_id:
                    await connection_manager.leave_group(user_id, group_id)

            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"未知消息类型: {msg_type}"},
                })

    except WebSocketDisconnect:
        logger.info(f"用户 {user_id} WebSocket 连接断开")
    except Exception as e:
        logger.error(f"WebSocket 错误 (用户 {user_id}): {e}")
    finally:
        await connection_manager.disconnect(websocket, user_id)
        await presence_tracker.set_offline(int(user_id))
