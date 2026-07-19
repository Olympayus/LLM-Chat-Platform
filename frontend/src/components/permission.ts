import type { Directive } from 'vue'

export const vPermission: Directive = {
  mounted(el, binding) {
    const permission = binding.value as string
    const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    if (!permissions.includes('*') && !permissions.includes(permission)) {
      el.parentNode?.removeChild(el)
    