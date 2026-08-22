import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '@/services/api'
import { ApiError } from '@/services/client'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { useLocalCollections } from '@/hooks/useLocalCollections'
import { ToolLogo } from '@/components/tools/ToolLogo'
import { PricingBadge } from '@/components/tools/PricingBadge'
import { FreeAccessList } from '@/components/tools/FreeAccessList'
import { ToolCard } from '@/components/tools/ToolCard'
import { ErrorState, SectionHeader, Skeleton, ToolGridSkeleton } from '@/components/ui/States'
import {
  CheckIcon,
  CrossIcon,
  ExternalIcon,
  HeartIcon,
  ScaleIcon,
  ShieldIcon,
  WarnIcon,
} from '@/components/ui/Icons'
import { cx, formatMonthYear, formatPrice } from '@/utils/format'
import type { FreeAccessGrant, PricingPlan, ToolDetail } from '@/types/api'
import { NotFoundPage } from './NotFoundPage'

export function ToolDetailPage() {
  const { slug = '' } = useParams()
  const { isFavorite, toggleFavorite, recordView, inCompare, toggleCompare, compareIsFull } =
    useLocalCollections()

  const tool = useQuery({
    queryKey: ['tool', slug],
    queryFn: () => api.tool(slug),
    enabled: Boolean(slug),
  })

  const alternatives = useQuery({
    queryKey: ['alternatives', slug],
    queryFn: () => api.alternatives(slug, 6),
    enabled: Boolean(tool.data),
  })

  const data = tool.data
  useEffect(() => {
    if (data) recordView(data.slug)
  }, [data, recordView])

  useDocumentMeta({
    title: data ? `${data.name} — ${data.tagline || 'AI developer tool'}` : 'Tool',
    description: data?.description,
    structuredData: data
      ? {
          '@context': 'https://schema.org',
          '@type': 'SoftwareApplication',
          name: data.name,
          description: data.description,
          url: data.website_url,
          applicationCategory: 'DeveloperApplication',
          offers: data.pricing_plans.length
            ? data.pricing_plans
                .filter((plan) => plan.price !== null)
                .map((plan) => ({
                  '@type': 'Offer',
                  name: plan.name,
                  price: plan.price,
                  priceCurrency: plan.currency,
                }))
            : undefined,
        }
      : null,
  })

  if (tool.error instanceof ApiError && tool.error.isNotFound) {
    return <NotFoundPage title="That tool is not in the catalogue" />
  }

  if (tool.error) {
    return (
      <div className="container-page py-12">
        <ErrorState error={tool.error} onRetry={() => tool.refetch()} />
      </div>
    )
  }

  if (!data) return <DetailSkeleton />

  const saved = isFavorite(data.slug)
  const comparing = inCompare(data.slug)
  const verified = formatMonthYear(data.verification.last_verified_at)

  return (
    <article className="container-page py-8">
      <nav className="mb-4 text-2xs text-faint">
        <Link to="/tools" className="hover:text-ink">
          Tools
        </Link>
        {data.categories[0] ? (
          <>
            <span className="mx-1.5">/</span>
            <Link to={`/category/${data.categories[0].slug}`} className="hover:text-ink">
              {data.categories[0].name}
            </Link>
          </>
        ) : null}
        <span className="mx-1.5">/</span>
        <span className="text-muted">{data.name}</span>
      </nav>

      <header className="flex flex-col gap-5 border-b border-line pb-7 sm:flex-row sm:items-start">
        <ToolLogo name={data.name} initials={data.initials} logoUrl={data.logo_url} size="lg" />
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{data.name}</h1>
          <p className="mt-1 text-muted">{data.tagline || data.description}</p>
          <div className="mt-3 flex flex-wrap items-center gap-1.5">
            <PricingBadge pricing={data.pricing} />
            <span className="badge text-muted">{data.pricing_headline}</span>
            {data.categories.map((category) => (
              <Link key={category.slug} to={`/category/${category.slug}`} className="badge text-muted hover:text-ink">
                {category.name}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 sm:flex-col">
          <a
            href={data.website_url}
            target="_blank"
            rel="noreferrer noopener"
            className="btn-primary"
          >
            Visit official website <ExternalIcon />
          </a>
          <button
            type="button"
            onClick={() => toggleFavorite(data.slug)}
            aria-pressed={saved}
            className={cx('btn-secondary', saved && 'text-negative')}
          >
            <HeartIcon filled={saved} /> {saved ? 'Saved' : 'Save'}
          </button>
          <button
            type="button"
            onClick={() => toggleCompare(data.slug)}
            disabled={!comparing && compareIsFull}
            className="btn-ghost"
          >
            <ScaleIcon /> {comparing ? 'In compare' : 'Compare'}
          </button>
        </div>
      </header>

      <div className="grid gap-8 py-8 lg:grid-cols-[1fr_20rem]">
        <div className="min-w-0 space-y-8">
          <section>
            <h2 className="section-title">Overview</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-muted">
              {data.long_description || data.description}
            </p>
          </section>

          <FreeAccessSection tool={data} />

          <PaidPlansSection tool={data} />

          {data.capabilities.length ? (
            <section>
              <h2 className="section-title">Capabilities</h2>
              <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                {data.capabilities.map((capability) => (
                  <li key={capability} className="flex items-start gap-2 text-sm text-muted">
                    <CheckIcon className="mt-0.5 shrink-0 text-positive" />
                    {capability}
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          <DeveloperSupport tool={data} />

          {data.best_for.length || data.not_ideal_for.length ? (
            <section className="grid gap-4 sm:grid-cols-2">
              {data.best_for.length ? (
                <div className="card p-4">
                  <h2 className="text-sm font-semibold">Best for</h2>
                  <ul className="mt-2 space-y-1.5">
                    {data.best_for.map((item) => (
                      <li key={item} className="flex items-start gap-2 text-sm text-muted">
                        <CheckIcon className="mt-0.5 shrink-0 text-positive" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {data.not_ideal_for.length ? (
                <div className="card p-4">
                  <h2 className="text-sm font-semibold">Not ideal for</h2>
                  <ul className="mt-2 space-y-1.5">
                    {data.not_ideal_for.map((item) => (
                      <li key={item} className="flex items-start gap-2 text-sm text-muted">
                        <CrossIcon className="mt-0.5 shrink-0 text-faint" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </section>
          ) : null}
        </div>

        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <section className="card p-4">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold">
              <ShieldIcon className="text-muted" /> Verification
            </h2>
            <dl className="mt-3 space-y-2 text-xs">
              <div className="flex justify-between gap-2">
                <dt className="text-faint">Last verified</dt>
                <dd className={cx(data.verification.is_stale ? 'text-caution' : 'text-muted')}>
                  {verified ?? 'Not verified'}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-faint">Source</dt>
                <dd className="truncate text-right">
                  {data.verification.source_url ? (
                    <a
                      href={data.verification.source_url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="link"
                    >
                      Provider page
                    </a>
                  ) : (
                    <span className="text-muted">Not recorded</span>
                  )}
                </dd>
              </div>
              {data.verification.note ? (
                <p className="pt-1 text-2xs text-faint">{data.verification.note}</p>
              ) : null}
              {data.verification.is_stale ? (
                <p className="flex items-start gap-1.5 rounded-lg bg-caution/10 p-2 text-2xs text-caution">
                  <WarnIcon className="mt-0.5 shrink-0" />
                  This record is over a year old. Confirm the current pricing on the provider's
                  site.
                </p>
              ) : null}
            </dl>
          </section>

          <QualitySection tool={data} />

          <section className="card p-4">
            <h2 className="text-sm font-semibold">Links</h2>
            <ul className="mt-2 space-y-1.5 text-xs">
              <LinkRow label="Official website" href={data.website_url} />
              <LinkRow label="Pricing page" href={data.pricing_url} />
              <LinkRow label="Documentation" href={data.docs_url} />
              <LinkRow label="Source repository" href={data.repo_url} />
            </ul>
          </section>
        </aside>
      </div>

      <section className="border-t border-line pt-8">
        <SectionHeader
          title="Alternatives"
          description={`Other tools that overlap with ${data.name}.`}
        />
        {alternatives.isPending ? <ToolGridSkeleton count={3} /> : null}
        {alternatives.data?.length ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {alternatives.data.map((alternative) => (
              <ToolCard key={alternative.slug} tool={alternative} compact />
            ))}
          </div>
        ) : alternatives.isFetched ? (
          <p className="card px-4 py-6 text-center text-sm text-muted">
            No close alternatives recorded yet.
          </p>
        ) : null}
      </section>
    </article>
  )
}

function FreeAccessSection({ tool }: { tool: ToolDetail }) {
  return (
    <section>
      <h2 className="section-title">Free access</h2>
      <div className="card mt-3 p-4">
        <p className="text-sm font-medium">{tool.free_access_headline}</p>
        {tool.free_access_summary ? (
          <p className="mt-1 text-sm text-muted">{tool.free_access_summary}</p>
        ) : null}

        <FreeAccessList lines={tool.free_access_lines} className="mt-3" />

        {tool.free_access_grants.length ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {tool.free_access_grants.map((grant) => (
              <GrantCard key={grant.id} grant={grant} />
            ))}
          </div>
        ) : null}

        <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-line pt-3 text-xs">
          <div>
            <dt className="text-faint">Credit card required</dt>
            <dd className="mt-0.5">{answer(tool.requires_credit_card)}</dd>
          </div>
          <div>
            <dt className="text-faint">Free access expires</dt>
            <dd className="mt-0.5">{answer(tool.free_access_expires)}</dd>
          </div>
        </dl>
      </div>
    </section>
  )
}

function GrantCard({ grant }: { grant: FreeAccessGrant }) {
  const allowance =
    grant.amount !== null
      ? `${grant.amount.toLocaleString()} ${grant.unit ?? ''}${grant.period ? ` / ${grant.period}` : ''}`
      : null

  return (
    <div className="rounded-lg border border-line bg-raised/50 p-3">
      <p className="text-2xs font-semibold uppercase tracking-wide text-faint">
        {grant.type.replace(/_/g, ' ').toLowerCase()}
      </p>
      {allowance ? <p className="mt-1 text-sm font-medium">{allowance}</p> : null}
      {grant.description ? <p className="mt-1 text-xs text-muted">{grant.description}</p> : null}
      {grant.restrictions.length ? (
        <ul className="mt-2 space-y-1">
          {grant.restrictions.map((restriction) => (
            <li key={restriction} className="flex items-start gap-1.5 text-2xs text-caution">
              <WarnIcon className="mt-0.5 shrink-0" />
              {restriction}
            </li>
          ))}
        </ul>
      ) : null}
      {grant.expires_after_days ? (
        <p className="mt-2 text-2xs text-faint">Expires after {grant.expires_after_days} days.</p>
      ) : null}
    </div>
  )
}

function PaidPlansSection({ tool }: { tool: ToolDetail }) {
  return (
    <section>
      <h2 className="section-title">Paid plans</h2>
      {tool.pricing_plans.length ? (
        <>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {tool.pricing_plans.map((plan) => (
              <PlanCard key={plan.id} plan={plan} />
            ))}
          </div>
          <p className="mt-3 text-2xs text-faint">
            Prices as published by the provider
            {formatMonthYear(tool.verification.last_verified_at)
              ? ` in ${formatMonthYear(tool.verification.last_verified_at)}`
              : ''}
            . Always confirm on the official pricing page before buying.
          </p>
        </>
      ) : (
        <div className="card mt-3 p-4">
          <p className="text-sm text-muted">
            {tool.pricing_summary ?? 'Pricing information unavailable.'}
          </p>
          <a
            href={tool.pricing_url ?? tool.website_url}
            target="_blank"
            rel="noreferrer noopener"
            className="btn-secondary mt-3"
          >
            Check the provider's pricing page <ExternalIcon />
          </a>
        </div>
      )}
    </section>
  )
}

function PlanCard({ plan }: { plan: PricingPlan }) {
  return (
    <div
      className={cx(
        'card p-4',
        plan.is_free && 'border-positive/40',
        plan.is_trial && 'border-caution/40',
      )}
    >
      <div className="flex items-baseline justify-between gap-2">
        <p className="font-medium">{plan.name}</p>
        {plan.is_trial ? <span className="badge text-caution">Trial</span> : null}
      </div>
      <p className="mt-1 text-xl font-semibold tabular-nums">
        {formatPrice(plan.price, plan.currency)}
        {plan.price ? (
          <span className="ml-1 text-xs font-normal text-faint">
            / {plan.is_per_seat ? 'user / month' : plan.billing_period}
          </span>
        ) : null}
      </p>
      {plan.description ? <p className="mt-2 text-xs text-muted">{plan.description}</p> : null}
      {plan.features.length ? (
        <ul className="mt-2 space-y-1">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-start gap-1.5 text-2xs text-muted">
              <CheckIcon className="mt-0.5 shrink-0 text-positive" />
              {feature}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}

function DeveloperSupport({ tool }: { tool: ToolDetail }) {
  const groups = [
    { title: 'Languages', items: tool.languages },
    { title: 'Platforms', items: tool.platforms },
    { title: 'Integrations', items: tool.integrations },
    { title: 'Features', items: tool.features },
  ].filter((group) => group.items.length)

  if (!groups.length) return null

  return (
    <section>
      <h2 className="section-title">Developer support</h2>
      <div className="mt-3 grid gap-4 sm:grid-cols-2">
        {groups.map((group) => (
          <div key={group.title}>
            <p className="text-2xs font-semibold uppercase tracking-wider text-faint">
              {group.title}
            </p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {group.items.map((item) => (
                <span key={item} className="badge text-muted">
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function QualitySection({ tool }: { tool: ToolDetail }) {
  return (
    <section className="card p-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-sm font-semibold">Record completeness</h2>
        <p className="text-sm font-semibold tabular-nums">
          {tool.quality.score}
          <span className="text-xs font-normal text-faint">/{tool.quality.max_score}</span>
        </p>
      </div>
      <p className="mt-1 text-2xs text-faint">
        How complete and fresh our record is — not a rating of the tool.
      </p>
      <ul className="mt-3 space-y-2">
        {tool.quality.components.map((component) => (
          <li key={component.key}>
            <div className="flex justify-between text-2xs">
              <span className="text-muted">{component.label}</span>
              <span className="tabular-nums text-faint">
                {component.score}/{component.max_score}
              </span>
            </div>
            <div className="mt-1 h-1 overflow-hidden rounded-full bg-raised">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${(component.score / component.max_score) * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function LinkRow({ label, href }: { label: string; href: string | null }) {
  if (!href) return null
  return (
    <li className="flex items-center justify-between gap-2">
      <span className="text-faint">{label}</span>
      <a href={href} target="_blank" rel="noreferrer noopener" className="link truncate">
        Open <ExternalIcon className="inline" />
      </a>
    </li>
  )
}

function answer(value: boolean | null): JSX.Element {
  if (value === null) return <span className="text-faint">Not recorded</span>
  return value ? (
    <span className="text-caution">Yes</span>
  ) : (
    <span className="text-positive">No</span>
  )
}

function DetailSkeleton() {
  return (
    <div className="container-page py-8">
      <div className="flex gap-5 border-b border-line pb-7">
        <Skeleton className="h-14 w-14 rounded-lg" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-7 w-56" />
          <Skeleton className="h-4 w-80" />
          <Skeleton className="h-5 w-64" />
        </div>
      </div>
      <div className="grid gap-8 py-8 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-11/12" />
          <Skeleton className="h-4 w-9/12" />
          <Skeleton className="h-40 w-full rounded-xl" />
        </div>
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    </div>
  )
}
