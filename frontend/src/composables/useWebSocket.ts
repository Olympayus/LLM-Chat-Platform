import { ref, onUnmounted } from 'vue'
import type { Message, WSMessage } from '../types/im'

/**
 * WebSocket 连接 Hook
 * 处理 IM 实时消息的收发、断线重连、心跳保活
 */
export function useWebSocket() {
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let token: string = ''

  const isConnected = ref(false)
  const messages = ref<Message[]>([])
  const lastMessage = ref<Message | null>(null)

  // 消息回调
  let onMessageCallback: ((msg: WSMessage) => void) | null = null
  let onRecallCallback: ((messageId: number, reason: string) => void) | null = null

  function connect(authToken: string) {
    token = authToken
    if (ws && ws.readyState === WebSocket.OPEN) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//localhost:8000/ws/im?token=${token}`

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      isConnected.value = true
      startHeartbeat()
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data: WSMessage = JSON.parse(event.data)
        handleWSMessage(data)
      } catch (e) {
        console.error('Failed to parse WS message:', e)
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      stopHeartbeat()
      scheduleReconnect()
    }

    ws.onerror = (error: Event) => {
      console.error('WebSocket error:', error)
      ws?.close()
    }
  }

  function handleWSMessage(data: WSMessage) {
    switch (data.type) {
      case 'message':
        // 新消息
        const msg = data.data as Message
        messages.value.push(msg)
        lastMessage.value = msg
        break

      case 'message_recall':
        // 消息撤回
        const { message_id, reason } = data.data
        const index = messages.value.findIndex(m => m.id === message_id)
        if (index !== -1) {
          messages.value[index].isRecalled = true
          messages.value[index].recallReason = reason || '消息已被撤回'
        }
        // 触发撤回回调
        if (onRecallCallback) {
          onRecallCallback(message_id, reason)
        }
        break

      case 'system_message':
        // 系统消息
        messages.value.push({
          id: Date.now(),
          chatType: 'group',
          senderType: 'system',
          senderId: 0,
          msgType: 'system',
          content: data.data.content,
          isRecalled: false,
          createdAt: new Date().toISOString(),
        })
        break

      case 'error':
        console.error('WS error:', data.data)
        break

      case 'ack':
        // 消息发送确认
        break
    }

    if (onMessageCallback) {
      onMessageCallback(data)
    }
  }

  function send(chatType: string, receiverId: number, content: string, msgType: string = 'text') {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return false
    }

    const payload = {
      type: 'message',
      data: {
        chat_type: chatType,
        receiver_id: receiverId,
        msg_type: msgType,
        content,
      },
    }

    ws.send(JSON.stringify(payload))
    return true
  }

  function disconnect() {
    stopHeartbeat()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    isConnected.value = false
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      if (token) {
        connect(token)
      }
    }, 3000) // 3秒后重连
  }

  function startHeartbeat() {
    stopHeartbeat()
    // 每30秒发送一次心跳
    heartbeatTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  // 设置消息回调
  function onMessage(callback: (msg: WSMessage) => void) {
    onMessageCallback = callback
  }

  // 设置撤回回调
  function onRecall(callback: (messageId: number, reason: string) => void) {
    onRecallCallback = callback
  }

  // 组件卸载时断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    messages,
    lastMessage,
    connect,
    send,
    disconnect,
    onMessage,
    onRecall,
  }
}