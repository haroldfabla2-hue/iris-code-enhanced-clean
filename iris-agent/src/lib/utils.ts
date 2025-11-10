import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date))
}

export function formatRelativeTime(date: string | Date) {
  const now = new Date()
  const targetDate = new Date(date)
  const diffInMs = now.getTime() - targetDate.getTime()
  
  const minutes = Math.floor(diffInMs / (1000 * 60))
  const hours = Math.floor(diffInMs / (1000 * 60 * 60))
  const days = Math.floor(diffInMs / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return "Justo ahora"
  if (minutes < 60) return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`
  if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`
  if (days < 7) return `Hace ${days} día${days > 1 ? 's' : ''}`
  
  return formatDate(date)
}

export function formatFileSize(bytes: number) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

export function generateId() {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  wait: number
): T {
  let timeout: NodeJS.Timeout | null = null
  
  return ((...args: any[]) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(() => func.apply(this, args), wait)
  }) as T
}

export function throttle<T extends (...args: any[]) => void>(
  func: T,
  limit: number
): T {
  let inThrottle: boolean
  
  return ((...args: any[]) => {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }) as T
}

export function isValidEmail(email: string) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + "..."
}

export function copyToClipboard(text: string) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text)
  } else {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'absolute'
    textArea.style.left = '-999999px'
    document.body.prepend(textArea)
    textArea.select()
    document.execCommand('copy')
    textArea.remove()
    return Promise.resolve()
  }
}

export function downloadFile(content: string, filename: string, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function getFileExtension(filename: string) {
  return filename.split('.').pop()?.toLowerCase() || ''
}

export function isImageFile(filename: string) {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']
  return imageExtensions.includes(getFileExtension(filename))
}

export function isCodeFile(filename: string) {
  const codeExtensions = ['js', 'jsx', 'ts', 'tsx', 'py', 'java', 'cpp', 'c', 'php', 'rb', 'go', 'rs', 'swift', 'kt']
  return codeExtensions.includes(getFileExtension(filename))
}

export function getLanguageFromExtension(filename: string): string {
  const ext = getFileExtension(filename)
  const languageMap: { [key: string]: string } = {
    'ts': 'typescript',
    'tsx': 'typescript',
    'js': 'javascript',
    'jsx': 'javascript',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'css': 'css',
    'html': 'html',
    'json': 'json',
    'md': 'markdown',
    'yaml': 'yaml',
    'yml': 'yaml',
    'xml': 'xml',
    'sql': 'sql',
    'sh': 'bash',
    'bash': 'bash',
  }
  return languageMap[ext] || 'plaintext'
}

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function getRandomColor() {
  const colors = [
    '#0066FF', '#10B981', '#F59E0B', '#EF4444', 
    '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

export function validateJson(str: string): boolean {
  try {
    JSON.parse(str)
    return true
  } catch {
    return false
  }
}

export function sanitizeHtml(html: string): string {
  // Basic HTML sanitization - in production, use a proper library like DOMPurify
  return html
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}