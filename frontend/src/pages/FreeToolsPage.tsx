import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { ToolCard } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'
import { ArrowRightIcon, GiftIcon } from '@/components/ui/Icons'
import { cx } from '@/utils/format'

const SEO_LINKS = [
  { to: '/free-ai-coding-tools', label: 'Free AI coding tools' },
  { to: '/free-ai-image-tools', label: 'Free AI image tools' },
  { to: '/free-ai-video-tools', label: 'Free AI video tools' },
  { to: '/free-ai-audio-tools', label: 'Free AI audio tools' },
  { to: '/free-ai-research-tools', label: 'Free AI research tools' },
]

export function FreeToolsPage({ presetCategory }: { presetCategory?: string }) {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeCategory = presetCategory ?? searchParams.get('category') ?? null

  const query = useQuery({
    queryKey: ['free-tools', activeCategory],
    queryFn: () => api.freeTools(activeCategory, 12),
  })

  const categoryName =
    query.data?.categories.find((category) => category.slug === activeCategory)?.name ?? null

  useDocumentMeta({
    title: categoryName ? `Free ${categoryName} AI tools` : 'Free AI tools for developers',
    description: categoryName
      ? `Free and open-source ${categoryName.toLowerCase()} AI tools, grouped by how they are free, with the actual limits listed.`
      : 'Free AI tools for developers: completely free, open source, generous free tiers, free credits and free developer APIs — with the real limits.',
  })

  const selectCategory = (slug: string | null) => {
    const next = new URLSearchParams(searchParams)
    if (slug) next.set('category', slug)
    else next.delete('category')
    setSearchParams(next, { replace: true })
  }

  return (
    <div className="container-page py-8">
      <header className="mb-6">
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <GiftIcon className="text-positive" />
          {categoryName ? `Free ${categoryName} tools` : 'Free AI tools'}
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-muted">
          Grouped by <em>how</em> they are free. A free trial is never presented as free forever,
          and where we do not know the exact limit we say so instead of guessing.
        </p>
        {query.data ? (
          <p className="mt-2 text-2xs text-faint">
            {query.data.total_free_tools} tools with some form of free access
            {categoryName ? ` in ${categoryName}` : ''}.
          </p>
        ) : null}
      </header>

      {presetCategory ? null : (
        <div className="mb-6 flex flex-wrap gap-1.5">
          <CategoryChip
            label="All categories"
            active={!activeCategory}
            onClick={() => selectCategory(null)}
          />
          {(query.data?.categories ?? []).map((category) => (
            <CategoryChip
              key={category.slug}
              label={`${category.name} (${category.free_tool_count})`}
              active={activeCategory === category.slug}
              onClick={() => selectCategory(category.slug)}
            />
          ))}
        </div>
      )}

      {query.isPending ? <ToolGridSkeleton count={6} /> : null}
      {query.error ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : null}

      {query.data ? (
        query.data.sections.length ? (
          <div className="space-y-12">
            {query.data.sections.map((section) => (
              <section key={section.slug}>
                <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
                  <div>
                    <h2 className="section-title">{section.title}</h2>
                    <p className="mt-1 text-sm text-muted">{section.description}</p>
                  </div>
                  {section.total > section.tools.length ? (
                    <Link
                      to={`/tools?${sectionFilterQuery(section.slug, activeCategory)}`}
                      className="btn-ghost text-sm"
                    >
                      All {section.total} <ArrowRightIcon />
                    </Link>
                  ) : null}
                </div>
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  {section.tools.map((tool) => (
                    <ToolCard key={tool.slug} tool={tool} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No free tools in this category yet"
            description="Try another category, or browse everything."
            action={
              <Link to="/tools?free_only=true" className="btn-secondary">
                All free tools
              </Link>
            }
          />
        )
      ) : null}

      <section className="mt-14 border-t border-line pt-6">
        <p className="text-2xs font-semibold uppercase tracking-wider text-faint">
          Popular free collections
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {SEO_LINKS.map((link) => (
            <Link key={link.to} to={link.to} className="badge px-2 py-1 text-xs text-muted hover:text-ink">
              {link.label}
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

/** Maps a free-tools section to the equivalent browse filters. */
function sectionFilterQuery(slug: string, category: string | null): string {
  const params = new URLSearchParams()
  const byPricing: Record<string, string> = {
    'completely-free': 'FREE_FOREVER',
    'open-source': 'OPEN_SOURCE',
    'generous-free-tiers': 'FREE_TIER',
    'free-credits': 'FREE_CREDITS',
  }
  if (slug === 'free-developer-apis') {
    params.set('has_free_api', 'true')
  } else if (byPricing[slug]) {
    params.set('pricing', byPricing[slug])
  } else {
    params.set('free_only', 'true')
  }
  if (category) params.set('category', category)
  params.set('sort', 'featured')
  return params.toString()
}

function CategoryChip({
  label,
  active,
  onClick,
}: {
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cx(
        'badge px-2 py-1 text-xs transition-colors',
        active ? 'border-accent bg-accent/10 text-accent' : 'text-muted hover:text-ink',
      )}
    >
      {label}
    </button>
  )
}
