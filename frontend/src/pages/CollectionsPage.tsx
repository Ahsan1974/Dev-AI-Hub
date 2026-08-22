import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { ErrorState, Skeleton } from '@/components/ui/States'
import { formatCount } from '@/utils/format'

export function CollectionsPage() {
  const query = useQuery({ queryKey: ['collections'], queryFn: () => api.collections() })

  useDocumentMeta({
    title: 'Curated AI tool collections',
    description:
      'Hand-picked AI toolkits for developers: free coding stacks, Java and Spring Boot toolkits, testing, architecture, DevOps, research and free APIs.',
  })

  return (
    <div className="container-page py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Collections</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted">
          Curated toolkits for a language, a stack or a job to be done. Every tool inside has been
          reviewed for that context, not just tagged.
        </p>
      </header>

      {query.isPending ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-32 rounded-xl" />
          ))}
        </div>
      ) : null}

      {query.error ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : null}

      {query.data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {query.data.map((collection) => (
            <Link
              key={collection.slug}
              to={`/collections/${collection.slug}`}
              className="card-interactive flex h-full flex-col p-5"
            >
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-medium">{collection.name}</h2>
                {collection.is_featured ? (
                  <span className="badge text-accent">Featured</span>
                ) : null}
              </div>
              {collection.description ? (
                <p className="mt-2 line-clamp-3 text-sm text-muted">{collection.description}</p>
              ) : null}
              <p className="mt-auto pt-4 text-2xs text-faint">
                {formatCount(collection.tool_count, 'tool')}
              </p>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  )
}
