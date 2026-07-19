import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, Conversation, Contact, GroupInfo } from '../types/im'
import axios from 'axios'

export const useIMStore = defineStore('im', () => {
  // 当前会话
  const currentConversation = ref<Conversation | null>(null)

  // 会话列表
  const conversations = ref<Conversation[]>([])
  
  // 联系人列表
  const contacts = ref<Contact[]>([])
  
  // 当前群组信息
  const currentGroup = ref<GroupInfo | null>(null)

  // JWT Token
  const token = ref<string>('')

  // 消息列表（按会话ID分组）
  const messageMap = ref<Map<number, Message[]>>(new Map())

  // 当前会话的消息
  const currentMessages = computed(() => {
    if (!currentConversation.value) return []
    const id = currentConversation.value.id
    return messageMap.value.get(id) || []
  })

  // 设置 Token
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('im_token', newToken)
  }

  // 初始化 Token（从 localStorage 恢复）
  function initToken() {
    const saved = localStorage.getItem('im_token')
    if (saved) {
      token.value = saved
    }
  }

  // 选择会话
  function selectConversation(conv: Conversation) {
    currentConversation.value = conv
    conv.unreadCount = 0

    // 如果是群聊，加载群信息
    if (conv.type === 'group') {
      loadGroupInfo(conv.id)
    } else {
      currentGroup.value = null
    }
  }

  // 添加消息到当前会话
  function addMessage(msg: Message) {
    if (!currentConversation.value) return
    const id = currentConversation.value.id
    if (!messageMap.value.has(id)) {
      messageMap.value.set(id, [])
    }
    messageMap.value.get(id)!.push(msg)
  }

  // 标记消息已撤回
  function markMessageRecalled(messageId: number, reason: string) {
    for (const [_, msgs] of messageMap.value) {
      const msg = msgs.find(m => m.id === messageId)
      if (msg) {
        msg.isRecalled = true
        msg.recallReason = reason
        break
      }
    }
  }

  // 加载会话列表
  async function loadConversations() {
    try {
      // [F-07/C] 由成员C提供IM会话列表API
      // 待成员C就绪后取消注释：
      // const res = await axios.get('/api/v1/im/contacts', {
      //   headers: { Authorization: `Bearer ${token.value}` }
      // })
      // conversations.value = res.data
      console.warn('loadConversations: 等待成员C提供IM API')
    } catch (e) {
      console.error('Failed to load conversations:', e)
    }
  }

  // 加载群信息
  async function loadGroupInfo(groupId: number) {
    try {
      const res = await axios.get(`/api/v1/admin/groups/${groupId}`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      currentGroup.value = res.data
    } catch (e) {
      console.error('Failed to load group info:', e)
    }
  }

  // 加载历史消息
  async function loadHistory(convId: number, page: number = 1) {
    try {
      if (!currentConversation.value) return
      const conv = currentConversation.value
      let url = ''
      if (conv.type === 'private') {
        url = `/api/v1/im/messages/private/${convId}`
      } else {
        url = `/api/v1/im/messages/group/${convId}`
      }
      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token.value}` },
        params: { page, page_size: 50 }
      })
      if (!messageMap.value.has(convId)) {
        messageMap.value.set(convId, [])
      }
      messageMap.value.set(convId, res.data.items || [])
    } catch (e) {
      console.error('Failed to load history:', e)
    }
  }

  return {
    currentConversation,
    conversations,
    contacts,
    currentGroup,
    token,
    currentMessages,
    setToken,
    in