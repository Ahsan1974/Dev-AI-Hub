import { useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api, type ToolQuery } from '@/services/api'
import { useToolFilters, type ToolFiltersState } from '@/hooks/useToolFilters'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { FilterSidebar } from '@/components/search/FilterSidebar'
import { FilterDrawer } from '@/components/search/FilterDrawer'
import { Pagination, ResultsToolbar } from '@/components/search/ResultsToolbar'
import { ToolGrid } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'

const PAGE_SIZE = 24

export function toQuery(filters: ToolFiltersState): ToolQuery {
  return { ...filters, page_size: PAGE_SIZE, q: filters.q || undefined }
}

export function BrowsePage() {
  const { filters, toggleValue, toggleBool, setSort, setPage, clearAll, activeCount } =
    useToolFilters()
  const [drawerOpen, setDrawerOpen] = useState(false)

  useDocumentMeta({
    title: 'Browse AI developer tools',
    description:
      'Browse every AI tool in DevAI Hub. Filter by pricing model, category, technology, feature, platform and capability.',
  })

  const query = useQuery({
    queryKey: ['tools', filters],
    queryFn: () => api.tools(toQuery(filters)),
    placeholderData: keepPreviousData,
  })

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
        <h1 className="text-2xl font-semibold tracking-tight">Browse tools</h1>
        <p className="mt-1 text-sm text-muted">
          Every tool in the catalogue, with its pricing status and free-access limits on the card.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[16rem_1fr]">
        <aside className="hidden lg:block">
          <div className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-1">
            {sidebar}
          </div>
        </aside>

        <section>
          <ResultsToolbar
            pagination={query.data?.pagination}
            sort={filters.sort}
            onSortChange={setSort}
            onOpenFilters={() => setDrawerOpen(true)}
            activeCount={activeCount}
          />

          {query.isPending ? <ToolGridSkeleton count={9} /> : null}
          {query.error ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : null}

          {query.data ? (
            query.data.data.length ? (
              <>
                <ToolGrid tools={query.data.data} />
                <Pagination pagination={query.data.pagination} onPageChange={setPage} />
              </>
            ) : (
              <EmptyState
                title="No tools match these filters"
                description="Try removing a filter, or widen the pricing selection."
                action={
                  activeCount ? (
                    <button type="button" className="btn-secondary" onClick={clearAll}>
                      Clear all filters
                    </button>
                  ) : null
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
