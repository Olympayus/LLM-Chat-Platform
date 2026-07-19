/** IM 消息类型定义 */

export interface Message {
  id: number
  chatType: 'private' | 'group'
  senderType: 'user' | 'bot' | 'system'
  senderId: number
  senderName?: string
  receiverId?: number
  groupId?: number
  msgType: 'text' | 'image' | 'file' | 'voice' | 'video' | 'system'
  content: string
  extra?: Record<string, any>
  isRecalled: boolean
  recallReason?: string
  createdAt: string
}

export interface Conversation {
  id: number
  type: 'private' | 'group'
  name: string
  avatar?: string
  lastMessage?: string
  lastTime?: string
  unreadCount: number
  isOnline?: boolean
}

export interface Contact {
  id: number
  userId: number
  username: string
  alias?: string
  avatar?: string
  isOnline: boolean
}

export interface GroupInfo {
  id: number
  groupName: string
  avatar?: string
  ownerId: number
  notice?: string
  memberCount: number
  members: GroupMember[]
}

export interface GroupMember {
  id: number
  userType: 'user' | 'bot'
  userId: number
  username?: string
  role: 'owner' | 'admin' | 'member'
}

export interface WSMessage {
  type: 'message' | 'message_recall' | 'system_message' | 'error' | 'ack'
  data: any
}