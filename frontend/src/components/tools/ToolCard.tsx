import { Link } from 'react-router-dom'
import type { ToolSummary } from '@/types/api'
import { capabilityChips, cx, formatMonthYear, toolPath } from '@/utils/format'
import { useLocalCollections } from '@/hooks/useLocalCollections'
import { ExternalIcon, HeartIcon, ScaleIcon } from '@/components/ui/Icons'
import { FreeAccessList } from './FreeAccessList'
import { PricingBadge } from './PricingBadge'
import { ToolLogo } from './ToolLogo'

interface ToolCardProps {
  tool: ToolSummary
  /** Optional ribbon such as "Best match" or a recommendation score. */
  highlight?: string
  reasons?: string[]
  compact?: boolean
}

export function ToolCard({ tool, highlight, reasons, compact = false }: ToolCardProps) {
  const { isFavorite, toggleFavorite, inCompare, toggleCompare, compareIsFull } =
    useLocalCollections()
  const saved = isFavorite(tool.slug)
  const comparing = inCompare(tool.slug)
  const compareDisabled = !comparing && compareIsFull
  const verified = formatMonthYear(tool.last_verified_at)
  const chips = capabilityChips(tool)
  const primaryCategory = tool.categories[0]

  return (
    <article
      className={cx(
        'card-interactive group flex h-full flex-col p-4',
        highlight && 'border-accent/60 ring-1 ring-accent/20',
      )}
    >
      {highlight ? (
        <p className="mb-3 -mt-1 text-2xs font-semibold uppercase tracking-wider text-accent">
          {highlight}
        </p>
      ) : null}

      <div className="flex items-start gap-3">
        <ToolLogo name={tool.name} initials={tool.initials} logoUrl={tool.logo_url} />
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-semibold leading-tight">
            <Link to={toolPath(tool.slug)} className="hover:text-accent">
              {tool.name}
            </Link>
          </h3>
          <p className="truncate text-xs text-muted">
            {tool.tagline || primaryCategory?.name || 'AI tool'}
          </p>
        </div>
        <button
          type="button"
          onClick={() => toggleFavorite(tool.slug)}
          aria-pressed={saved}
          aria-label={saved ? `Remove ${tool.name} from favorites` : `Save ${tool.name}`}
          title={saved ? 'Remove from favorites' : 'Save to favorites'}
          className={cx(
            'rounded-md p-1.5 transition-colors',
            saved ? 'text-negative' : 'text-faint hover:bg-raised hover:text-ink',
          )}
        >
          <HeartIcon filled={saved} className="text-base" />
        </button>
      </div>

      <p className="mt-3 line-clamp-2 text-sm text-muted">{tool.description}</p>

      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <PricingBadge pricing={tool.pricing} />
        <span className="text-2xs text-faint">{tool.pricing_headline}</span>
      </div>

      {!compact ? (
        <div className="mt-3 rounded-lg border border-line bg-raised/60 p-2.5">
          <p className="mb-1 text-2xs font-medium uppercase tracking-wide text-faint">
            Free access
          </p>
          {tool.free_access_lines.length ? (
            <FreeAccessList lines={tool.free_access_lines} dense />
          ) : (
            <p className="text-2xs text-muted">{tool.free_access_headline}</p>
          )}
        </div>
      ) : null}

      {reasons?.length ? (
        <ul className="mt-3 space-y-1">
          {reasons.slice(0, 4).map((reason) => (
            <li key={reason} className="flex items-center gap-1.5 text-xs text-muted">
              <span aria-hidden="true" className="text-positive">
                ✓
              </span>
              {reason}
            </li>
          ))}
        </ul>
      ) : null}

      {tool.languages.length ? (
        <p className="mt-3 truncate text-2xs text-faint" title={tool.languages.join(', ')}>
          {tool.languages.slice(0, 5).join(' • ')}
          {tool.languages.length > 5 ? ` • +${tool.languages.length - 5}` : ''}
        </p>
      ) : null}

      {chips.length ? (
        <div className="mt-2 flex flex-wrap gap-1">
          {chips.map((chip) => (
            <span key={chip} className="badge text-muted">
              {chip}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-auto pt-4">
        <div className="flex items-center gap-2">
          <Link to={toolPath(tool.slug)} className="btn-secondary flex-1">
            View details
          </Link>
          <a
            href={tool.website_url}
            target="_blank"
            rel="noreferrer noopener"
            className="btn-ghost"
            aria-label={`Open the official ${tool.name} website`}
          >
            Website <ExternalIcon />
          </a>
        </div>
        <div className="mt-2 flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => toggleCompare(tool.slug)}
            disabled={compareDisabled}
            title={compareDisabled ? 'You can compare up to 4 tools' : undefined}
            className={cx(
              'inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-2xs font-medium transition-colors',
              comparing ? 'text-accent' : 'text-faint hover:text-ink',
              compareDisabled && 'cursor-not-allowed opacity-50',
            )}
          >
            <ScaleIcon /> {comparing ? 'In compare' : 'Compare'}
          </button>
          <span className="text-2xs text-faint">
            {verified ? `Verified ${verified}` : 'Not verified yet'}
          </span>
        </div>
      </div>
    </article>
  )
}

export function ToolGrid({
  tools,
  columns = 3,
  compact = false,
}: {
  tools: ToolSummary[]
  columns?: 2 | 3 | 4
  compact?: boolean
}) {
  const layout = {
    2: 'sm:grid-cols-2',
    3: 'sm:grid-cols-2 xl:grid-cols-3',
    4: 'sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4',
  }[columns]

  return (
    <div className={cx('grid gap-4', layout)}>
      {tools.map((tool) => (
        <ToolCard key={tool.slug} tool={tool} compact={compact} />
      ))}
    </div>
  )
}
