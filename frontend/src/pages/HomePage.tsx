import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { useLocalCollections } from '@/hooks/useLocalCollections'
import { ToolCard } from '@/components/tools/ToolCard'
import { SearchHero } from '@/components/search/SearchHero'
import { ErrorState, SectionHeader, ToolGridSkeleton } from '@/components/ui/States'
import { ArrowRightIcon, WorkflowIcon } from '@/components/ui/Icons'
import { formatCount } from '@/utils/format'
import type { CategoryWithCount, Collection, ToolSummary, Workflow } from '@/types/api'

export function HomePage() {
  const { recent } = useLocalCollections()
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['home'],
    queryFn: api.home,
  })

  const { data: recentTools } = useQuery({
    queryKey: ['resolve-tools', recent.map((item) => item.slug).slice(0, 8)],
    queryFn: () => api.resolveTools(recent.map((item) => item.slug).slice(0, 8)),
    enabled: recent.length > 0,
  })

  useDocumentMeta({
    title: 'DevAI Hub',
    description:
      'Discover the right AI tools for every developer task. Search, compare and pick from AI tools for coding, testing, research, design, image, video and audio — with real free-tier limits.',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'DevAI Hub',
      url: window.location.origin,
      potentialAction: {
        '@type': 'SearchAction',
        target: `${window.location.origin}/search?q={search_term_string}`,
        'query-input': 'required name=search_term_string',
      },
    },
  })

  return (
    <div className="container-page">
      <section className="border-b border-line py-14 sm:py-20">
        <div className="mx-auto max-w-3xl text-center">
          <span className="badge mx-auto mb-5 w-fit px-2 py-1 text-muted">
            Developer-first · free-first · {data ? formatCount(data.stats.tools, 'tool') : 'curated'}
          </span>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">
            Discover the Best AI Tools for Developers
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-muted">
            Find AI tools for coding, testing, research, design, image, video, audio and
            productivity — with the free limits, the real price and the date we checked.
          </p>
          <div className="mx-auto mt-8 max-w-2xl text-left">
            <SearchHero popular={data?.popular_searches ?? []} />
          </div>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            <Link to="/what-do-i-need" className="btn-secondary">
              Describe your task instead
            </Link>
            <Link to="/free-tools" className="btn-ghost">
              Browse free tools <ArrowRightIcon />
            </Link>
          </div>
        </div>
      </section>

      {error ? (
        <div className="py-10">
          <ErrorState error={error} onRetry={() => refetch()} />
        </div>
      ) : null}

      {isLoading ? (
        <div className="py-10">
          <ToolGridSkeleton count={6} />
        </div>
      ) : null}

      {data ? (
        <div className="space-y-14 py-12">
          <StatsRow
            stats={[
              { label: 'Tools', value: data.stats.tools },
              { label: 'With free access', value: data.stats.free_tools },
              { label: 'Categories', value: data.stats.categories },
              { label: 'Verified records', value: data.stats.verified_tools },
            ]}
          />

          <Workflows workflows={data.workflows} />

          <section>
            <SectionHeader
              title="Featured free tools"
              description="Completely free, open source, or with a free tier you can actually build on."
              action={
                <Link to="/free-tools" className="btn-ghost text-sm">
                  All free tools <ArrowRightIcon />
                </Link>
              }
            />
            <ToolRow tools={data.featured_free} />
          </section>

          <PopularCategories categories={data.popular_categories} />

          <section>
            <SectionHeader
              title="Recently added"
              description="The newest records in the catalogue, by the date they entered the database."
              action={
                <Link to="/tools?sort=newest" className="btn-ghost text-sm">
                  Browse newest <ArrowRightIcon />
                </Link>
              }
            />
            <ToolRow tools={data.recently_added} />
          </section>

          {data.favorites_available && data.developer_favorites.length ? (
            <section>
              <SectionHeader
                title="Developer favorites"
                description="Ranked by how many people saved these tools here. No invented popularity numbers."
              />
              <ToolRow tools={data.developer_favorites} />
            </section>
          ) : null}

          {recentTools?.length ? (
            <section>
              <SectionHeader
                title="Pick up where you left off"
                description="Tools you opened recently, stored only in this browser."
                action={
                  <Link to="/favorites#recent" className="btn-ghost text-sm">
                    See all <ArrowRightIcon />
                  </Link>
                }
              />
              <ToolRow tools={recentTools} />
            </section>
          ) : null}

          <CollectionsRow collections={data.collections} />
        </div>
      ) : null}
    </div>
  )
}

function StatsRow({ stats }: { stats: Array<{ label: string; value: number }> }) {
  return (
    <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label} className="card px-4 py-3">
          <dt className="text-2xs uppercase tracking-wider text-faint">{stat.label}</dt>
          <dd className="mt-1 text-2xl font-semibold tabular-nums">{stat.value}</dd>
        </div>
      ))}
    </dl>
  )
}

function Workflows({ workflows }: { workflows: Workflow[] }) {
  if (!workflows.length) return null
  return (
    <section>
      <SectionHeader
        title="What developers need"
        description="Start from the task. Each one runs a curated search."
      />
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
        {workflows.map((workflow) => (
          <Link
            key={workflow.slug}
            to={`/search?q=${encodeURIComponent(workflow.query)}`}
            className="card-interactive group flex flex-col gap-2 p-3.5"
            title={workflow.description}
          >
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-raised text-base text-muted transition-colors group-hover:text-accent">
              <WorkflowIcon name={workflow.icon} />
            </span>
            <span className="text-sm font-medium leading-tight">{workflow.label}</span>
            <span className="line-clamp-2 text-2xs text-faint">{workflow.description}</span>
          </Link>
        ))}
      </div>
    </section>
  )
}

function PopularCategories({ categories }: { categories: CategoryWithCount[] }) {
  if (!categories.length) return null
  return (
    <section>
      <SectionHeader
        title="Popular categories"
        description="Every category shows how many of its tools have free access."
        action={
          <Link to="/tools" className="btn-ghost text-sm">
            All categories <ArrowRightIcon />
          </Link>
        }
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {categories.map((category) => (
          <Link
            key={category.slug}
            to={`/category/${category.slug}`}
            className="card-interactive flex items-center justify-between gap-3 p-4"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{category.name}</p>
              <p className="mt-0.5 text-2xs text-faint">{category.group}</p>
            </div>
            <div className="shrink-0 text-right">
              <p className="text-sm font-semibold tabular-nums">{category.tool_count}</p>
              <p className="text-2xs text-positive">{category.free_tool_count} free</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}

function CollectionsRow({ collections }: { collections: Collection[] }) {
  if (!collections.length) return null
  return (
    <section>
      <SectionHeader
        title="Curated collections"
        description="Hand-picked toolkits for a language, a stack or a job to be done."
        action={
          <Link to="/collections" className="btn-ghost text-sm">
            All collections <ArrowRightIcon />
          </Link>
        }
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {collections.map((collection) => (
          <Link
            key={collection.slug}
            to={`/collections/${collection.slug}`}
            className="card-interactive flex flex-col p-4"
          >
            <p className="font-medium">{collection.name}</p>
            {collection.description ? (
              <p className="mt-1 line-clamp-2 text-sm text-muted">{collection.description}</p>
            ) : null}
            <p className="mt-3 text-2xs text-faint">{formatCount(collection.tool_count, 'tool')}</p>
          </Link>
        ))}
      </div>
    </section>
  )
}

/** Horizontal-feeling grid capped at six cards for homepage sections. */
function ToolRow({ tools }: { tools: ToolSummary[] }) {
  if (!tools.length) {
    return <p className="card px-4 py-8 text-center text-sm text-muted">Nothing here yet.</p>
  }
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {tools.slice(0, 6).map((tool) => (
        <ToolCard key={tool.slug} tool={tool} />
      ))}
    </div>
  )
}
