import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { ToolQuery } from '@/services/api'

export const MULTI_KEYS = [
  'category',
  'technology',
  'feature',
  'platform',
  'integration',
  'pricing',
] as const

export const BOOL_KEYS = [
  'free_only',
  'open_source',
  'has_api',
  'has_free_api',
  'has_mcp',
  'has_agent',
  'has_local_model',
] as const

export type MultiKey = (typeof MULTI_KEYS)[number]
export type BoolKey = (typeof BOOL_KEYS)[number]

export interface ToolFiltersState extends ToolQuery {
  q: string
  sort: string
  page: number
}

const DEFAULT_SORT = 'featured'

/** Keeps the filter state in the URL so every result view is shareable. */
export function useToolFilters(defaults: Partial<ToolFiltersState> = {}) {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters = useMemo<ToolFiltersState>(() => {
    const state: ToolFiltersState = {
      q: searchParams.get('q') ?? defaults.q ?? '',
      sort: searchParams.get('sort') ?? defaults.sort ?? DEFAULT_SORT,
      page: Number(searchParams.get('page') ?? 1) || 1,
    }
    for (const key of MULTI_KEYS) {
      const values = searchParams.getAll(key)
      if (values.length) state[key] = values
    }
    for (const key of BOOL_KEYS) {
      if (searchParams.get(key) === 'true') state[key] = true
    }
    if (defaults.free_only && !searchParams.has('free_only')) state.free_only = true
    return state
  }, [searchParams, defaults.q, defaults.sort, defaults.free_only])

  const update = useCallback(
    (mutate: (params: URLSearchParams) => void, { resetPage = true } = {}) => {
      const next = new URLSearchParams(searchParams)
      mutate(next)
      if (resetPage) next.delete('page')
      setSearchParams(next, { replace: true })
    },
    [searchParams, setSearchParams],
  )

  const toggleValue = useCallback(
    (key: MultiKey, value: string) => {
      update((params) => {
        const current = params.getAll(key)
        params.delete(key)
        const next = current.includes(value)
          ? current.filter((item) => item !== value)
          : [...current, value]
        next.forEach((item) => params.append(key, item))
      })
    },
    [update],
  )

  const toggleBool = useCallback(
    (key: BoolKey) => {
      update((params) => {
        if (params.get(key) === 'true') params.delete(key)
        else params.set(key, 'true')
      })
    },
    [update],
  )

  const setQuery = useCallback(
    (value: string) => {
      update((params) => {
        if (value.trim()) params.set('q', value)
        else params.delete('q')
      })
    },
    [update],
  )

  const setSort = useCallback(
    (value: string) => {
      update((params) => {
        if (value && value !== DEFAULT_SORT) params.set('sort', value)
        else params.delete('sort')
      })
    },
    [update],
  )

  const setPage = useCallback(
    (page: number) => {
      update(
        (params) => {
          if (page > 1) params.set('page', String(page))
          else params.delete('page')
        },
        { resetPage: false },
      )
    },
    [update],
  )

  const clearAll = useCallback(() => {
    update((params) => {
      const q = params.get('q')
      Array.from(params.keys()).forEach((key) => params.delete(key))
      if (q) params.set('q', q)
    })
  }, [update])

  const activeCount = useMemo(() => {
    let count = 0
    for (const key of MULTI_KEYS) count += searchParams.getAll(key).length
    for (const key of BOOL_KEYS) if (searchParams.get(key) === 'true') count += 1
    return count
  }, [searchParams])

  return { filters, toggleValue, toggleBool, setQuery, setSort, setPage, clearAll, activeCount }
}
