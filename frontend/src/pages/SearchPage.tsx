import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useToolFilters } from '@/hooks/useToolFilters'
import { useDebounced } from '@/hooks/useDebounced'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { FilterSidebar } from '@/components/search/FilterSidebar'
import { FilterDrawer } from '@/components/search/FilterDrawer'
import { Pagination, ResultsToolbar } from '@/components/search/ResultsToolbar'
import { ToolGrid } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'
import { SearchIcon, SparkIcon } from '@/components/ui/Icons'
import { toQuery } from './BrowsePage'

export function SearchPage() {
  const { filters, toggleValue, toggleBool, setQuery, setSort, setPage, clearAll, activeCount } =
    useToolFilters({ sort: 'relevance' })
  const [term, setTerm] = useState(filters.q)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const debouncedTerm = useDebounced(term, 300)

  // The input owns the text; the URL catches up once typing settles.
  useEffect(() => {
    if (debouncedTerm !== filters.q) setQuery(debouncedTerm)
  }, [debouncedTerm, filters.q, setQuery])

  useEffect(() => setTerm(filters.q), [filters.q])

  useDocumentMeta({
    title: filters.q ? `${filters.q} — search` : 'Search AI developer tools',
    description: filters.q
      ? `AI developer tools matching "${filters.q}", ranked by relevance with free-access limits shown.`
      : 'Search AI tools by name, description, category, technology, feature or free-access wording.',
  })

  const search = useQuery({
    queryKey: ['search', filters],
    queryFn: () => api.search(toQuery(filters)),
    placeholderData: keepPreviousData,
  })

  const meta = search.data?.meta
  const sidebar = (
    <FilterSidebar
      filters={filters}
      onToggleValue={toggleValue}
      onToggleBool={toggleBool}
      onClear={clearAll}
      activeCount={activeCount}
    />
  )

  return (
    <div className="container-page py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Search</h1>
        <div className="relative mt-3 max-w-2xl">
          <SearchIcon className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-base text-faint" />
          <input
            type="search"
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder="Search tools... e.g. free java testing AI"
            aria-label="Search tools"
            autoFocus
            className="input h-11 pl-10"
          />
        </div>

        {meta && filters.q ? (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-2xs text-faint">
            {meta.interpreted_keywords.length ? (
              <span>
                Matching on{' '}
                <span className="font-mono text-muted">
                  {meta.interpreted_keywords.join(', ')}
                </span>
              </span>
            ) : null}
            {meta.detected_free_intent ? (
              <span className="badge border-positive/40 text-positive">
                Free-only filter applied
              </span>
            ) : null}
            <span>· {meta.took_ms} ms</span>
          </div>
        ) : null}
      </header>

      <div className="grid gap-6 lg:grid-cols-[16rem_1fr]">
        <aside className="hidden lg:block">
          <div className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-1">
            {sidebar}
          </div>
        </aside>

        <section>
          <ResultsToolbar
            pagination={search.data?.pagination}
            sort={filters.sort}
            onSortChange={setSort}
            onOpenFilters={() => setDrawerOpen(true)}
            activeCount={activeCount}
            label="result"
          />

          {search.isPending ? <ToolGridSkeleton count={9} /> : null}
          {search.error ? (
            <ErrorState error={search.error} onRetry={() => search.refetch()} />
          ) : null}

          {search.data ? (
            search.data.data.length ? (
              <>
                <ToolGrid tools={search.data.data} />
                <Pagination pagination={search.data.pagination} onPageChange={setPage} />
              </>
            ) : (
              <EmptyState
                title={filters.q ? `Nothing matched “${filters.q}”` : 'No tools match these filters'}
                icon={<SearchIcon className="text-base" />}
                description={
                  meta?.suggestions.length ? (
                    <span>
                      Try one of these instead:{' '}
                      {meta.suggestions.map((suggestion, index) => (
                        <span key={suggestion}>
                          {index > 0 ? ', ' : ''}
                          <Link
                            className="link"
                            to={`/search?q=${encodeURIComponent(suggestion)}`}
                          >
                            {suggestion}
                          </Link>
                        </span>
                      ))}
                    </span>
                  ) : (
                    'Try fewer words, or describe the task in the "What do I need?" page instead.'
                  )
                }
                action={
                  <div className="flex gap-2">
                    {activeCount ? (
                      <button type="button" className="btn-secondary" onClick={clearAll}>
                        Clear filters
                      </button>
                    ) : null}
                    <Link
                      to={`/what-do-i-need${filters.q ? `?q=${encodeURIComponent(filters.q)}` : ''}`}
                      className="btn-primary"
                    >
                      <SparkIcon /> Describe your task
                    </Link>
                  </div>
                }
              />
            )
          ) : null}
        </section>
      </div>

      <FilterDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        {sidebar}
      </FilterDrawer>
    </div>
  )
}
