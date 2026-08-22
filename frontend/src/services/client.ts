/** Thin fetch wrapper that understands the backend's response envelopes. */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details?: Record<string, unknown>

  constructor(status: number, code: string, message: string, details?: Record<string, unknown>) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }

  get isNotFound() {
    return this.status === 404
  }
}

export type QueryValue = string | number | boolean | null | undefined | string[]

export function buildQuery(params: Record<string, QueryValue>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    if (Array.isArray(value)) {
      value.filter(Boolean).forEach((item) => search.append(key, item))
    } else {
      search.append(key, String(value))
    }
  }
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {}, signal } = options

  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      signal,
      headers: {
        Accept: 'application/json',
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (cause) {
    if ((cause as Error).name === 'AbortError') throw cause
    throw new ApiError(
      0,
      'NETWORK_ERROR',
      'Could not reach the DevAI Hub API. Is the backend running on port 8000?',
    )
  }

  if (response.status === 204) return undefined as T

  const payload = await response.json().catch(() => null)

  if (!response.ok) {
    const error = (payload as { error?: { code?: string; message?: string; details?: Record<string, unknown> } })
      ?.error
    throw new ApiError(
      response.status,
      error?.code ?? 'UNEXPECTED_ERROR',
      error?.message ?? 'Something went wrong while talking to the API.',
      error?.details,
    )
  }

  return payload as T
}

/** Unwraps `{ "data": ... }` envelopes returned by single-resource endpoints. */
export async function requestData<T>(path: string, options?: RequestOptions): Promise<T> {
  const payload = await request<{ data: T }>(path, options)
  return payload.data
}
