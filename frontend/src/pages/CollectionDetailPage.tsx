import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '@/services/api'
import { ApiError } from '@/services/client'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { ToolGrid } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'
import { formatCount } from '@/utils/format'
import { NotFoundPage } from './NotFoundPage'

export function CollectionDetailPage() {
  const { slug = '' } = useParams()
  const query = useQuery({
    queryKey: ['collection', slug],
    queryFn: () => api.collection(slug),
    enabled: Boolean(slug),
  })

  useDocumentMeta({
    title: query.data?.name ?? 'Collection',
    description: query.data?.description ?? 'A curated collection of AI tools for developers.',
    structuredData: query.data
      ? {
          '@context': 'https://schema.org',
          '@type': 'ItemList',
          name: query.data.name,
          description: query.data.description,
          numberOfItems: query.data.tools.length,
          itemListElement: query.data.tools.map((tool, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            name: tool.name,
            url: tool.website_url,
          })),
        }
      : null,
  })

  if (query.error instanceof ApiError && query.error.isNotFound) {
    return <NotFoundPage title="That collection does not exist" />
  }

  if (query.error) {
    return (
      <div className="container-page py-12">
        <ErrorState error={query.error} onRetry={() => query.refetch()} />
      </div>
    )
  }

  return (
    <div className="container-page py-8">
      <nav className="mb-3 text-2xs text-faint">
        <Link to="/collections" className="hover:text-ink">
          Collections
        </Link>
        <span className="mx-1.5">/</span>
        <span className="text-muted">{query.data?.name ?? slug}</span>
      </nav>

      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">{query.data?.name ?? 'Collection'}</h1>
        {query.data?.description ? (
          <p className="mt-1 max-w-2xl text-sm text-muted">{query.data.description}</p>
        ) : null}
        {query.data ? (
          <p className="mt-2 text-2xs text-faint">{formatCount(query.data.tools.length, 'tool')}</p>
        ) : null}
      </header>

      {query.isPending ? <ToolGridSkeleton count={6} /> : null}

      {query.data ? (
        query.data.tools.length ? (
          <ToolGrid tools={query.data.tools} />
        ) : (
          <EmptyState
            title="This collection is empty"
            description="No tools have been added to it yet."
          />
        )
      ) : null}
    </div>
  )
}
