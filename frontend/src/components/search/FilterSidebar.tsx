import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { cx } from '@/utils/format'
import { Skeleton } from '@/components/ui/States'
import type { BoolKey, MultiKey, ToolFiltersState } from '@/hooks/useToolFilters'

interface FilterSidebarProps {
  filters: ToolFiltersState
  onToggleValue: (key: MultiKey, value: string) => void
  onToggleBool: (key: BoolKey) => void
  onClear: () => void
  activeCount: number
  /** Category page already scopes results, so its facet is hidden there. */
  hideCategories?: boolean
}

interface Option {
  value: string
  label: string
  count?: number
}

const CAPABILITY_TOGGLES: Array<{ key: BoolKey; label: string }> = [
  { key: 'free_only', label: 'Free access only' },
  { key: 'open_source', label: 'Open source' },
  { key: 'has_api', label: 'Has an API' },
  { key: 'has_free_api', label: 'Free API tier' },
  { key: 'has_agent', label: 'Agent mode' },
  { key: 'has_mcp', label: 'MCP support' },
  { key: 'has_local_model', label: 'Runs local models' },
]

export function FilterSidebar({
  filters,
  onToggleValue,
  onToggleBool,
  onClear,
  activeCount,
  hideCategories = false,
}: FilterSidebarProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['filters'],
    queryFn: api.filters,
    staleTime: 10 * 60 * 1000,
  })

  if (isLoading || !data) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="card space-y-2 p-4">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-5/6" />
            <Skeleton className="h-3 w-2/3" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold">Filters</p>
        {activeCount > 0 ? (
          <button type="button" onClick={onClear} className="text-2xs text-accent hover:underline">
            Clear all ({activeCount})
          </button>
        ) : null}
      </div>

      <FilterGroup title="Capabilities" defaultOpen>
        <div className="space-y-1.5">
          {CAPABILITY_TOGGLES.map((toggle) => (
            <CheckRow
              key={toggle.key}
              label={toggle.label}
              checked={Boolean(filters[toggle.key])}
              onChange={() => onToggleBool(toggle.key)}
            />
          ))}
        </div>
      </FilterGroup>

      <FilterGroup title="Pricing" defaultOpen>
        <OptionList
          options={data.pricing.map((item) => ({
            value: item.value,
            label: item.label,
            count: item.count,
          }))}
          selected={filters.pricing ?? []}
          onToggle={(value) => onToggleValue('pricing', value)}
        />
      </FilterGroup>

      {!hideCategories ? (
        <FilterGroup title="Category" searchable>
          {(term) => (
            <OptionList
              options={toOptions(data.categories, term)}
              selected={filters.category ?? []}
              onToggle={(value) => onToggleValue('category', value)}
            />
          )}
        </FilterGroup>
      ) : null}

      <FilterGroup title="Technology" searchable>
        {(term) => (
          <OptionList
            options={toOptions(data.technologies, term)}
            selected={filters.technology ?? []}
            onToggle={(value) => onToggleValue('technology', value)}
          />
        )}
      </FilterGroup>

      <FilterGroup title="Features" searchable>
        {(term) => (
          <OptionList
            options={toOptions(data.features, term)}
            selected={filters.feature ?? []}
            onToggle={(value) => onToggleValue('feature', value)}
          />
        )}
      </FilterGroup>

      <FilterGroup title="Platform">
        <OptionList
          options={toOptions(data.platforms, '')}
          selected={filters.platform ?? []}
          onToggle={(value) => onToggleValue('platform', value)}
        />
      </FilterGroup>

      <FilterGroup title="Integrations">
        <OptionList
          options={toOptions(data.integrations, '')}
          selected={filters.integration ?? []}
          onToggle={(value) => onToggleValue('integration', value)}
        />
      </FilterGroup>
    </div>
  )
}

function toOptions(
  items: Array<{ slug: string; name: string; tool_count: number }>,
  term: string,
): Option[] {
  const needle = term.trim().toLowerCase()
  return items
    .filter((item) => !needle || item.name.toLowerCase().includes(needle))
    .map((item) => ({ value: item.slug, label: item.name, count: item.tool_count }))
}

function FilterGroup({
  title,
  children,
  defaultOpen = false,
  searchable = false,
}: {
  title: string
  children: React.ReactNode | ((term: string) => React.ReactNode)
  defaultOpen?: boolean
  searchable?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  const [term, setTerm] = useState('')

  return (
    <section className="card overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium hover:bg-raised"
      >
        {title}
        <span className={cx('text-faint transition-transform', open && 'rotate-90')}>›</span>
      </button>
      {open ? (
        <div className="border-t border-line px-4 py-3">
          {searchable ? (
            <input
              type="search"
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              placeholder={`Filter ${title.toLowerCase()}...`}
              aria-label={`Filter ${title} options`}
              className="input mb-2 py-1.5 text-xs"
            />
          ) : null}
          <div className="max-h-64 overflow-y-auto pr-1">
            {typeof children === 'function' ? children(term) : children}
          </div>
        </div>
      ) : null}
    </section>
  )
}

function OptionList({
  options,
  selected,
  onToggle,
}: {
  options: Option[]
  selected: string[]
  onToggle: (value: string) => void
}) {
  if (!options.length) {
    return <p className="py-2 text-2xs text-faint">No matching options.</p>
  }
  return (
    <div className="space-y-1.5">
      {options.map((option) => (
        <CheckRow
          key={option.value}
          label={option.label}
          count={option.count}
          checked={selected.includes(option.value)}
          onChange={() => onToggle(option.value)}
        />
      ))}
    </div>
  )
}

function CheckRow({
  label,
  count,
  checked,
  onChange,
}: {
  label: string
  count?: number
  checked: boolean
  onChange: () => void
}) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-xs">
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="h-3.5 w-3.5 shrink-0 rounded border-line bg-surface accent-accent"
      />
      <span className={cx('flex-1 truncate', checked ? 'text-ink' : 'text-muted')}>{label}</span>
      {count !== undefined ? <span className="text-2xs tabular-nums text-faint">{count}</span> : null}
    </label>
  )
}
