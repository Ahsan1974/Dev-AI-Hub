import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { useLocalCollections } from '@/hooks/useLocalCollections'
import { ToolGrid } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, SectionHeader, ToolGridSkeleton } from '@/components/ui/States'
import { ClockIcon, HeartIcon } from '@/components/ui/Icons'

export function FavoritesPage() {
  const { favorites, recent, clearFavorites, clearRecent } = useLocalCollections()
  const recentSlugs = recent.map((entry) => entry.slug)

  useDocumentMeta({
    title: 'Your saved tools',
    description: 'Tools you saved and recently viewed, stored in this browser only.',
  })

  const saved = useQuery({
    queryKey: ['resolve-tools', favorites],
    queryFn: () => api.resolveTools(favorites),
    enabled: favorites.length > 0,
  })

  const viewed = useQuery({
    queryKey: ['resolve-tools', recentSlugs],
    queryFn: () => api.resolveTools(recentSlugs),
    enabled: recentSlugs.length > 0,
  })

  return (
    <div className="container-page py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Your tools</h1>
        <p className="mt-1 text-sm text-muted">
          Saved and recently viewed tools live in this browser. No account, no sign-in — clearing
          site data clears them.
        </p>
      </header>

      <section className="mb-14">
        <SectionHeader
          title="Favorites"
          description={favorites.length ? `${favorites.length} saved` : undefined}
          action={
            favorites.length ? (
              <button type="button" onClick={clearFavorites} className="btn-ghost text-sm">
                Clear favorites
              </button>
            ) : null
          }
        />
        {!favorites.length ? (
          <EmptyState
            title="No saved tools yet"
            icon={<HeartIcon className="text-base" />}
            description="Tap the heart on any tool card to keep it here."
            action={
              <Link to="/tools" className="btn-secondary">
                Browse tools
              </Link>
            }
          />
        ) : saved.isPending ? (
          <ToolGridSkeleton count={3} />
        ) : saved.error ? (
          <ErrorState error={saved.error} onRetry={() => saved.refetch()} />
        ) : (
          <ToolGrid tools={saved.data ?? []} />
        )}
      </section>

      <section id="recent" className="scroll-mt-20">
        <SectionHeader
          title="Recently viewed"
          description={recentSlugs.length ? `Last ${recentSlugs.length} tools you opened` : undefined}
          action={
            recentSlugs.length ? (
              <button type="button" onClick={clearRecent} className="btn-ghost text-sm">
                Clear history
              </button>
            ) : null
          }
        />
        {!recentSlugs.length ? (
          <EmptyState
            title="Nothing viewed yet"
            icon={<ClockIcon className="text-base" />}
            description="Tools you open will appear here so you can get back to them."
          />
        ) : viewed.isPending ? (
          <ToolGridSkeleton count={3} />
        ) : viewed.error ? (
          <ErrorState error={viewed.error} onRetry={() => viewed.refetch()} />
        ) : (
          <ToolGrid tools={viewed.data ?? []} compact />
        )}
      </section>
    </div>
  )
}
