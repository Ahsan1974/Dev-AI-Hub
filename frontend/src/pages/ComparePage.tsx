import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { useLocalCollections, MAX_COMPARE } from '@/hooks/useLocalCollections'
import { ToolLogo } from '@/components/tools/ToolLogo'
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/States'
import { CheckIcon, CrossIcon, ExternalIcon, ScaleIcon, SearchIcon } from '@/components/ui/Icons'
import { comparePath, cx, parseComparePath } from '@/utils/format'
import { useDebounced } from '@/hooks/useDebounced'
import type { CompareCell, CompareRow } from '@/types/api'

export function ComparePage() {
  const { pair } = useParams()
  const navigate = useNavigate()
  const { compare, removeFromCompare, clearCompare, toggleCompare } = useLocalCollections()

  const fromUrl = useMemo(() => parseComparePath(pair), [pair])
  const slugs = fromUrl.length ? fromUrl : compare

  // A shared /compare/a-vs-b link seeds the local shortlist.
  useEffect(() => {
    if (!fromUrl.length) return
    fromUrl.slice(0, MAX_COMPARE).forEach((slug) => {
      if (!compare.includes(slug)) toggleCompare(slug)
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pair])

  useDocumentMeta({
    title: slugs.length >= 2 ? `Compare ${slugs.join(' vs ')}` : 'Compare AI tools',
    description:
      'Compare up to four AI developer tools side by side: free status, free allowance, pricing, open source, API, agent, MCP, local models, languages and platforms.',
  })

  const comparison = useQuery({
    queryKey: ['compare', slugs],
    queryFn: () => api.compare(slugs),
    enabled: slugs.length >= 2,
  })

  const remove = (slug: string) => {
    removeFromCompare(slug)
    const next = slugs.filter((item) => item !== slug)
    navigate(next.length >= 2 ? comparePath(next) : '/compare', { replace: true })
  }

  return (
    <div className="container-page py-8">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Compare tools</h1>
          <p className="mt-1 text-sm text-muted">
            Up to {MAX_COMPARE} tools side by side. Blank cells mean we have not verified that
            detail — never that the answer is no.
          </p>
        </div>
        {slugs.length ? (
          <button
            type="button"
            className="btn-ghost"
            onClick={() => {
              clearCompare()
              navigate('/compare', { replace: true })
            }}
          >
            Clear
          </button>
        ) : null}
      </header>

      <ToolPicker selected={slugs} />

      {slugs.length < 2 ? (
        <div className="mt-6">
          <EmptyState
            title="Pick at least two tools"
            icon={<ScaleIcon className="text-base" />}
            description="Add tools from any card's Compare button, or search for them above."
            action={
              <Link to="/tools" className="btn-secondary">
                Browse tools
              </Link>
            }
          />
        </div>
      ) : null}

      {comparison.isPending && slugs.length >= 2 ? (
        <div className="mt-6 space-y-2">
          <Skeleton className="h-28 w-full rounded-xl" />
          <Skeleton className="h-96 w-full rounded-xl" />
        </div>
      ) : null}

      {comparison.error ? (
        <div className="mt-6">
          <ErrorState error={comparison.error} onRetry={() => comparison.refetch()} />
        </div>
      ) : null}

      {comparison.data ? (
        <div className="mt-6">
          {comparison.data.missing_slugs.length ? (
            <p className="mb-4 rounded-lg border border-caution/40 bg-caution/10 px-3 py-2 text-xs text-caution">
              Not in the catalogue: {comparison.data.missing_slugs.join(', ')}
            </p>
          ) : null}

          {comparison.data.tools.length >= 2 ? (
            <div className="overflow-x-auto rounded-xl border border-line">
              <table className="w-full min-w-[42rem] border-collapse text-sm">
                <thead className="bg-surface">
                  <tr>
                    <th className="w-40 border-b border-line px-3 py-3 text-left align-bottom text-2xs font-semibold uppercase tracking-wider text-faint sm:w-52">
                      Attribute
                    </th>
                    {comparison.data.tools.map((tool) => (
                      <th
                        key={tool.slug}
                        className="border-b border-l border-line px-3 py-3 text-left align-top"
                      >
                        <div className="flex items-start gap-2">
                          <ToolLogo
                            name={tool.name}
                            initials={tool.initials}
                            logoUrl={tool.logo_url}
                            size="sm"
                          />
                          <div className="min-w-0">
                            <Link
                              to={`/tools/${tool.slug}`}
                              className="block truncate font-medium hover:text-accent"
                            >
                              {tool.name}
                            </Link>
                            <p className="truncate text-2xs font-normal text-faint">
                              {tool.tagline}
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => remove(tool.slug)}
                            className="ml-auto rounded p-1 text-faint hover:text-ink"
                            aria-label={`Remove ${tool.name}`}
                          >
                            <CrossIcon />
                          </button>
                        </div>
                        <a
                          href={tool.website_url}
                          target="_blank"
                          rel="noreferrer noopener"
                          className="mt-2 inline-flex items-center gap-1 text-2xs font-normal text-accent hover:underline"
                        >
                          Website <ExternalIcon />
                        </a>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>{renderRows(comparison.data.rows)}</tbody>
              </table>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

function renderRows(rows: CompareRow[]) {
  const output: JSX.Element[] = []
  let currentGroup = ''

  rows.forEach((row) => {
    if (row.group !== currentGroup) {
      currentGroup = row.group
      output.push(
        <tr key={`group-${row.group}`} className="bg-raised/60">
          <td
            colSpan={row.cells.length + 1}
            className="border-b border-line px-3 py-1.5 text-2xs font-semibold uppercase tracking-wider text-faint"
          >
            {row.group}
          </td>
        </tr>,
      )
    }
    output.push(
      <tr key={row.key} className="align-top">
        <th
          scope="row"
          className="border-b border-line px-3 py-2.5 text-left text-xs font-medium text-muted"
        >
          {row.label}
        </th>
        {row.cells.map((cell, index) => (
          <td key={index} className="border-b border-l border-line px-3 py-2.5 text-xs">
            <Cell cell={cell} />
          </td>
        ))}
      </tr>,
    )
  })

  return output
}

function Cell({ cell }: { cell: CompareCell }) {
  if (cell.kind === 'bool') {
    return cell.value ? (
      <CheckIcon className="text-base text-positive" aria-label="Yes" />
    ) : (
      <CrossIcon className="text-base text-faint" aria-label="No" />
    )
  }

  if (cell.kind === 'unknown' || cell.value === null || cell.value === undefined) {
    return (
      <span className="text-faint" title={cell.note ?? 'Not verified'}>
        —
      </span>
    )
  }

  if (cell.kind === 'list' && Array.isArray(cell.value)) {
    if (!cell.value.length) return <span className="text-faint">—</span>
    return (
      <div className="flex flex-wrap gap-1">
        {cell.value.map((item) => (
          <span key={item} className="badge text-muted">
            {item}
          </span>
        ))}
      </div>
    )
  }

  return (
    <span className={cx(cell.kind === 'price' && 'font-medium tabular-nums')}>
      {String(cell.value)}
      {cell.note ? <span className="mt-0.5 block text-2xs text-faint">{cell.note}</span> : null}
    </span>
  )
}

/** Typeahead that adds tools to the comparison without leaving the page. */
function ToolPicker({ selected }: { selected: string[] }) {
  const [term, setTerm] = useState('')
  const debounced = useDebounced(term, 250)
  const navigate = useNavigate()
  const { toggleCompare, compareIsFull } = useLocalCollections()

  const results = useQuery({
    queryKey: ['compare-picker', debounced],
    queryFn: () => api.search({ q: debounced, page_size: 6, sort: 'relevance' }),
    enabled: debounced.trim().length > 1,
  })

  const add = (slug: string) => {
    toggleCompare(slug)
    setTerm('')
    const next = [...selected, slug].slice(0, MAX_COMPARE)
    if (next.length >= 2) navigate(comparePath(next), { replace: true })
  }

  return (
    <div className="relative max-w-md">
      <SearchIcon className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-faint" />
      <input
        type="search"
        value={term}
        onChange={(event) => setTerm(event.target.value)}
        placeholder={compareIsFull ? `Maximum of ${MAX_COMPARE} tools` : 'Add a tool to compare...'}
        aria-label="Add a tool to the comparison"
        disabled={compareIsFull}
        className="input pl-9"
      />
      {results.data && debounced.trim().length > 1 ? (
        <ul className="absolute z-20 mt-1 w-full overflow-hidden rounded-lg border border-line bg-surface shadow-lg">
          {results.data.data.length ? (
            results.data.data
              .filter((tool) => !selected.includes(tool.slug))
              .map((tool) => (
                <li key={tool.slug}>
                  <button
                    type="button"
                    onClick={() => add(tool.slug)}
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-raised"
                  >
                    <ToolLogo
                      name={tool.name}
                      initials={tool.initials}
                      logoUrl={tool.logo_url}
                      size="sm"
                    />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate">{tool.name}</span>
                      <span className="block truncate text-2xs text-faint">{tool.tagline}</span>
                    </span>
                  </button>
                </li>
              ))
          ) : (
            <li className="px-3 py-2 text-xs text-faint">No tools found.</li>
          )}
        </ul>
      ) : null}
    </div>
  )
}
