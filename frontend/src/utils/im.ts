/**
 * IM 工具函数
 * 提供日期格式化、消息分组等通用工具
 */

/**
 * 格式化消息时间
 * @param dateStr ISO 日期字符串或 Date 对象
 * @returns 格式化后时间字符串
 *
 * 规则:
 * - 今天: 显示 时:分 (14:30)
 * - 昨天: 显示 "昨天 时:分"
 * - 本周: 显示 "周X 时:分"
 * - 更早: 显示 "月-日 时:分"
 */
export function formatMessageTime(dateStr: string | Date): string {
  const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const targetDay = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.floor((today.getTime() - targetDay.getTime()) / (1000 * 60 * 60 * 24))

  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const timeStr = `${hours}:${minutes}`

  if (diffDays === 0) {
    return timeStr // 今天
  } else if (diffDays === 1) {
    return `昨天 ${timeStr}`
  } else if (diffDays < 7) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${weekdays[date.getDay()]} ${timeStr}`
  } else {
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}-${day} ${timeStr}`
  }
}

/**
 * 格式化会话列表时间
 * @param dateStr ISO 日期字符串
 * @returns 简短时间字符串
 */
export function formatConversationTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / (1000 * 60))

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour}小时前`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay}天前`

  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${month}-${day}`
}

/**
 * 按日期对消息进行分组
 * @param messages 消息列表
 * @returns 分组后的消息 { date: string, items: Message[] }
 */
export function groupMessagesByDate<T extends { createdAt: string }>(
  messages: T[]
): { date: string; items: T[] }[] {
  const groups: Map<string, T[]> = new Map()

  for (const msg of messages) {
    const date = new Date(msg.createdAt)
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const msgDay = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const diffDays = Math.floor((today.getTime() - msgDay.getTime()) / (1000 * 60 * 60 * 24))

    let label: string
    if (diffDays === 0) {
      label = '今天'
    } else if (diffDays === 1) {
      label = '昨天'
    } else if (diffDays < 7) {
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      label = weekdays[date.getDay()]
    } else {
      label = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
    }

    if (!groups.has(label)) {
      groups.set(label, [])
    }
    groups.get(label)!.push(msg)
  }

  return Array.from(groups.entries()).map(([date, items]) => ({ date, items }))
}

/**
 * 判断两条消息是否连续（时间差 < 5分钟，且发送者相同）
 * @param prevMsg 上一条消息
 * @param currMsg 当前消息
 * @returns 是否连续
 */
export function isMessageConsecutive<T extends { senderId: number; createdAt: string }>(
  prevMsg: T | null,
  currMsg: T
): boolean {
  if (!prevMsg) return false
  if (prevMsg.senderId !== currMsg.senderId) return false

  const prevTime = new Date(prevMsg.createdAt).getTime()
  const currTime = new Date(currMsg.createdAt).getTime()
  return (currTime - prevTime) < 5 * 60 * 1000
}

/**
 * 截断长文本
 * @param text 原始文本
 * @param maxLen 最大长度
 * @returns 截断后文本
 */
export function truncateText(