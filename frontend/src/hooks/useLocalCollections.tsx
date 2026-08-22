import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  RECENT_LIMIT,
  StorageKey,
  readJson,
  writeJson,
  type RecentEntry,
} from '@/utils/storage'

export const MAX_COMPARE = 4

interface LocalCollectionsValue {
  favorites: string[]
  isFavorite: (slug: string) => boolean
  toggleFavorite: (slug: string) => void
  clearFavorites: () => void

  recent: RecentEntry[]
  recordView: (slug: string) => void
  clearRecent: () => void

  compare: string[]
  inCompare: (slug: string) => boolean
  toggleCompare: (slug: string) => void
  removeFromCompare: (slug: string) => void
  clearCompare: () => void
  compareIsFull: boolean
}

const LocalCollectionsContext = createContext<LocalCollectionsValue | null>(null)

export function LocalCollectionsProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<string[]>(() => readJson(StorageKey.favorites, []))
  const [recent, setRecent] = useState<RecentEntry[]>(() => readJson(StorageKey.recent, []))
  const [compare, setCompare] = useState<string[]>(() => readJson(StorageKey.compare, []))

  useEffect(() => writeJson(StorageKey.favorites, favorites), [favorites])
  useEffect(() => writeJson(StorageKey.recent, recent), [recent])
  useEffect(() => writeJson(StorageKey.compare, compare), [compare])

  // Keep other tabs of the same browser consistent.
  useEffect(() => {
    const onStorage = (event: StorageEvent) => {
      if (event.key === StorageKey.favorites) setFavorites(readJson(StorageKey.favorites, []))
      if (event.key === StorageKey.recent) setRecent(readJson(StorageKey.recent, []))
      if (event.key === StorageKey.compare) setCompare(readJson(StorageKey.compare, []))
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const toggleFavorite = useCallback((slug: string) => {
    setFavorites((current) =>
      current.includes(slug) ? current.filter((item) => item !== slug) : [slug, ...current],
    )
  }, [])

  const recordView = useCallback((slug: string) => {
    setRecent((current) =>
      [{ slug, viewedAt: Date.now() }, ...current.filter((item) => item.slug !== slug)].slice(
        0,
        RECENT_LIMIT,
      ),
    )
  }, [])

  const toggleCompare = useCallback((slug: string) => {
    setCompare((current) => {
      if (current.includes(slug)) return current.filter((item) => item !== slug)
      if (current.length >= MAX_COMPARE) return current
      return [...current, slug]
    })
  }, [])

  const value = useMemo<LocalCollectionsValue>(
    () => ({
      favorites,
      isFavorite: (slug) => favorites.includes(slug),
      toggleFavorite,
      clearFavorites: () => setFavorites([]),
      recent,
      recordView,
      clearRecent: () => setRecent([]),
      compare,
      inCompare: (slug) => compare.includes(slug),
      toggleCompare,
      removeFromCompare: (slug) => setCompare((current) => current.filter((item) => item !== slug)),
      clearCompare: () => setCompare([]),
      compareIsFull: compare.length >= MAX_COMPARE,
    }),
    [favorites, recent, compare, toggleFavorite, recordView, toggleCompare],
  )

  return (
    <LocalCollectionsContext.Provider value={value}>{children}</LocalCollectionsContext.Provider>
  )
}

export function useLocalCollections(): LocalCollectionsValue {
  const context = useContext(LocalCollectionsContext)
  if (!context) {
    throw new Error('useLocalCollections must be used inside LocalCollectionsProvider')
  }
  return context
}
