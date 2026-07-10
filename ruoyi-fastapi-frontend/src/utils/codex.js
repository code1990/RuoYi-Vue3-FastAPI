import { getToken } from '@/utils/auth'

const RUNNING_STATUS = new Set(['running', 'queued', 'pending', 'submitted', 'started', 'in_progress', 'processing'])
const SUCCESS_STATUS = new Set(['done', 'completed', 'success', 'succeeded', 'finished', 'ok'])
const ERROR_STATUS = new Set(['error', 'failed', 'failure', 'timeout', 'canceled', 'cancelled'])

export function getStatusTone(status, hasError = false) {
  if (hasError) {
    return 'danger'
  }

  const normalized = normalizeStatus(status)
  if (RUNNING_STATUS.has(normalized)) {
    return 'warning'
  }
  if (SUCCESS_STATUS.has(normalized)) {
    return 'success'
  }
  if (ERROR_STATUS.has(normalized)) {
    return 'danger'
  }
  return 'info'
}

export function normalizeStatus(status) {
  return String(status || '').trim().toLowerCase()
}

export function formatMsTime(value) {
  if (!value && value !== 0) {
    return '--'
  }

  const date = new Date(Number(value))
  if (Number.isNaN(date.getTime())) {
    return '--'
  }

  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hour = pad(date.getHours())
  const minute = pad(date.getMinutes())
  const second = pad(date.getSeconds())
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

export function formatCount(value) {
  return Number.isFinite(Number(value)) ? Number(value) : 0
}

export function toPrettyJson(value) {
  try {
    return JSON.stringify(typeof value === 'string' ? JSON.parse(value) : value, null, 2)
  } catch (_) {
    return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
  }
}

export function parsePayloadJson(value) {
  if (!value) {
    return null
  }

  try {
    return JSON.parse(value)
  } catch (_) {
    return value
  }
}

export async function openCodexStream({ conversationId, pollIntervalMs = 1000, onData, signal }) {
  const response = await fetch(createCodexStreamUrl(conversationId, pollIntervalMs), {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${getToken()}`
    },
    signal
  })

  if (!response.ok || !response.body) {
    throw new Error(`Stream request failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''

    for (const block of blocks) {
      const event = parseSseEvent(block)
      if (event && onData) {
        onData(event)
      }
    }
  }

  if (buffer.trim()) {
    const event = parseSseEvent(buffer)
    if (event && onData) {
      onData(event)
    }
  }

  return true
}

function createCodexStreamUrl(conversationId, pollIntervalMs = 1000) {
  const baseUrl = `${import.meta.env.VITE_APP_BASE_API}/codex/conversations/${conversationId}/stream`
  return `${baseUrl}?pollIntervalMs=${pollIntervalMs}`
}

function parseSseEvent(rawBlock) {
  const lines = rawBlock.split('\n')
  let eventName = 'message'
  const dataLines = []

  lines.forEach((line) => {
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim())
    }
  })

  if (!dataLines.length) {
    return null
  }

  const rawData = dataLines.join('\n')
  try {
    return {
      event: eventName,
      data: JSON.parse(rawData)
    }
  } catch (_) {
    return null
  }
}

function pad(value) {
  return String(value).padStart(2, '0')
}
