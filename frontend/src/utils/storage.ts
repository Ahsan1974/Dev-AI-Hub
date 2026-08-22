/** localStorage helpers. Everything degrades to a no-op in private mode. */

const PREFIX = 'devai-hub'

export const StorageKey = {
  theme: `${PREFIX}:theme`,
  favorites: `${PREFIX}:favorites`,
  recent: `${PREFIX}:recently-viewed`,
  compare: `${PREFIX}:compare`,
  clientId: `${PREFIX}:client-id`,
} as const

export function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

export function writeJson(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* quota or privacy mode - saving is best effort */
  }
}

export interface RecentEntry {
  slug: string
  viewedAt: number
}

export const RECENT_LIMIT = 20

export function clientId(): string {
  try {
    const existing = window.localStorage.getItem(StorageKey.clientId)
    if (existing) return existing
    const generated =
      typeof crypto !== 'undefined' && 'randomUUID' in crypto
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2) + Date.now().toString(36)
    window.localStorage.setItem(StorageKey.clientId, generated)
    return generated
  } catch {
    return 'anonymous'
  }
}
