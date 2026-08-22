import { useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '@/services/api'
import { useToolFilters } from '@/hooks/useToolFilters'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { FilterSidebar } from '@/components/search/FilterSidebar'
import { FilterDrawer } from '@/components/search/FilterDrawer'
import { Pagination, ResultsToolbar } from '@/components/search/ResultsToolbar'
import { ToolGrid } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'
import { toQuery } from './BrowsePage'

export function CategoryPage() {
  const { slug = '' } = useParams()
  const { filters, toggleValue, toggleBool, setSort, setPage, clearAll, activeCount } =
    useToolFilters()
  const [drawerOpen, setDrawerOpen] = useState(false)

  const category = useQuery({
    queryKey: ['category', slug],
    queryFn: () => api.category(slug),
  })

  const tools = useQuery({
    queryKey: ['category-tools', slug, filters],
    queryFn: () => api.categoryTools(slug, toQuery(filters)),
    placeholderData: keepPreviousData,
    enabled: Boolean(slug),
  })

  useDocumentMeta({
    title: category.data ? `${category.data.name} AI tools` : 'Category',
    description:
      category.data?.description ??
      `AI developer tools in the ${slug.replace(/-/g, ' ')} category, with free-access details.`,
  })

  const sidebar = (
    <FilterSidebar
      filters={filters}
      onToggleValue={toggleValue}
      onToggleBool={toggleBool}
      onClear={clearAll}
      activeCount={activeCount}
      hideCategories
    />
  )

  if (category.error) {
    return (
      <div className="container-page py-12">
        <ErrorState error={category.error} onRetry={() => category.refetch()} />
      </div>
    )
  }

  return (
    <div className="container-page py-8">
      <nav className="mb-3 text-2xs text-faint">
        <Link to="/tools" className="hover:text-ink">
          Tools
        </Link>
        <span className="mx-1.5">/</span>
        <span className="text-muted">{category.data?.name ?? slug}</span>
      </nav>

      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">
          {category.data?.name ?? 'Category'}
        </h1>
        {category.data?.description ? (
          <p className="mt-1 max-w-2xl text-sm text-muted">{category.data.description}</p>
        ) : null}
        {category.data ? (
          <p className="mt-2 text-2xs text-faint">
            {category.data.tool_count} tools · {category.data.free_tool_count} with free access ·{' '}
            <Link
              to={`/free-tools?category=${category.data.slug}`}
              className="text-accent hover:underline"
            >
              free ones only
            </Link>
          </p>
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
            pagination={tools.data?.pagination}
            sort={filters.sort}
            onSortChange={setSort}
            onOpenFilters={() => setDrawerOpen(true)}
            activeCount={activeCount}
          />

          {tools.isPending ? <ToolGridSkeleton count={6} /> : null}
          {tools.error ? <ErrorState error={tools.error} onRetry={() => tools.refetch()} /> : null}

          {tools.data ? (
            tools.data.data.length ? (
              <>
                <ToolGrid tools={tools.data.data} />
                <Pagination pagination={tools.data.pagination} onPageChange={setPage} />
              </>
            ) : (
              <EmptyState
                title="No tools match these filters"
                description="This category has tools, but not with the filters you selected."
                action={
                  activeCount ? (
                    <button type="button" className="btn-secondary" onClick={clearAll}>
                      Clear filters
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
