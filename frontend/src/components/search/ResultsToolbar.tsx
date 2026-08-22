import type { PaginationMeta } from '@/types/api'
import { cx } from '@/utils/format'
import { FilterIcon } from '@/components/ui/Icons'

const SORTS = [
  { value: 'featured', label: 'Featured' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'newest', label: 'Newest' },
  { value: 'most_free', label: 'Most free' },
  { value: 'verified', label: 'Recently verified' },
  { value: 'name', label: 'Name (A–Z)' },
]

export function ResultsToolbar({
  pagination,
  sort,
  onSortChange,
  onOpenFilters,
  activeCount,
  label = 'tool',
}: {
  pagination?: PaginationMeta
  sort: string
  onSortChange: (value: string) => void
  onOpenFilters?: () => void
  activeCount: number
  label?: string
}) {
  const total = pagination?.total ?? 0
  const from = pagination ? (pagination.page - 1) * pagination.page_size + 1 : 0
  const to = pagination ? Math.min(pagination.page * pagination.page_size, total) : 0

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <p className="text-sm text-muted">
        {total > 0 ? (
          <>
            <span className="font-medium text-ink tabular-nums">
              {from}–{to}
            </span>{' '}
            of <span className="tabular-nums">{total}</span> {label}
            {total === 1 ? '' : 's'}
          </>
        ) : (
          'No results'
        )}
      </p>

      <div className="flex items-center gap-2">
        {onOpenFilters ? (
          <button type="button" onClick={onOpenFilters} className="btn-secondary py-1.5 lg:hidden">
            <FilterIcon /> Filters
            {activeCount > 0 ? (
              <span className="rounded-full bg-accent px-1.5 text-2xs text-accent-ink">
                {activeCount}
              </span>
            ) : null}
          </button>
        ) : null}
        <label className="flex items-center gap-2 text-xs text-muted">
          <span className="hidden sm:inline">Sort</span>
          <select
            value={sort}
            onChange={(event) => onSortChange(event.target.value)}
            className="input w-auto py-1.5 text-xs"
            aria-label="Sort results"
          >
            {SORTS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
    </div>
  )
}

export function Pagination({
  pagination,
  onPageChange,
}: {
  pagination: PaginationMeta
  onPageChange: (page: number) => void
}) {
  if (pagination.total_pages <= 1) return null

  const { page, total_pages: totalPages } = pagination
  const pages = pageWindow(page, totalPages)

  return (
    <nav className="mt-8 flex items-center justify-center gap-1" aria-label="Pagination">
      <button
        type="button"
        className="btn-secondary px-2.5 py-1.5 text-xs"
        disabled={!pagination.has_previous}
        onClick={() => onPageChange(page - 1)}
      >
        Previous
      </button>
      {pages.map((item, index) =>
        item === null ? (
          <span key={`gap-${index}`} className="px-1 text-xs text-faint">
            …
          </span>
        ) : (
          <button
            key={item}
            type="button"
            onClick={() => onPageChange(item)}
            aria-current={item === page ? 'page' : undefined}
            className={cx(
              'min-w-8 rounded-lg border px-2 py-1.5 text-xs tabular-nums transition-colors',
              item === page
                ? 'border-accent bg-accent text-accent-ink'
                : 'border-line bg-surface text-muted hover:bg-raised hover:text-ink',
            )}
          >
            {item}
          </button>
        ),
      )}
      <button
        type="button"
        className="btn-secondary px-2.5 py-1.5 text-xs"
        disabled={!pagination.has_next}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </button>
    </nav>
  )
}

function pageWindow(current: number, total: number): Array<number | null> {
  const pages = new Set<number>([1, total, current, current - 1, current + 1])
  const sorted = [...pages].filter((page) => page >= 1 && page <= total).sort((a, b) => a - b)

  const output: Array<number | null> = []
  let previous = 0
  for (const page of sorted) {
    if (previous && page - previous > 1) output.push(null)
    output.push(page)
    previous = page
  }
  return output
}
