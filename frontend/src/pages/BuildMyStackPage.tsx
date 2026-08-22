import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { ToolCard } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/States'
import { StackIcon } from '@/components/ui/Icons'
import { cx } from '@/utils/format'
import type { Budget, StackResponse } from '@/types/api'

const BUDGETS: Array<{ value: Budget; label: string }> = [
  { value: 'free_only', label: 'Free only' },
  { value: 'mostly_free', label: 'Mostly free' },
  { value: 'any', label: 'Any price' },
]

const GOALS = [
  'developer productivity',
  'ship faster',
  'code quality',
  'learning',
  'automation',
  'cost control',
]

export function BuildMyStackPage() {
  const [language, setLanguage] = useState('')
  const [frameworks, setFrameworks] = useState<string[]>([])
  const [ide, setIde] = useState('')
  const [goals, setGoals] = useState<string[]>([])
  const [budget, setBudget] = useState<Budget>('free_only')
  const [areas, setAreas] = useState<string[]>([])
  const [result, setResult] = useState<StackResponse | null>(null)

  useDocumentMeta({
    title: 'Build my AI developer stack',
    description:
      'Answer five questions and get a personal AI developer stack: coding, agents, debugging, testing, review, docs, research, UI, DevOps and productivity.',
  })

  const { data: filters } = useQuery({
    queryKey: ['filters'],
    queryFn: api.filters,
    staleTime: 10 * 60 * 1000,
  })
  const { data: meta } = useQuery({ queryKey: ['meta'], queryFn: api.meta, staleTime: Infinity })

  const build = useMutation({
    mutationFn: () =>
      api.buildStack({
        primary_language: language || null,
        frameworks,
        ide: ide || null,
        goals,
        budget,
        include_areas: areas,
      }),
    onSuccess: setResult,
  })

  const technologies = filters?.technologies ?? []
  const platforms = filters?.platforms ?? []
  const stackAreas = meta?.stack_areas ?? []

  return (
    <div className="container-page py-8">
      <header className="mx-auto max-w-2xl text-center">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Build your AI developer stack
        </h1>
        <p className="mt-2 text-sm text-muted">
          One pick per job, chosen with the same scoring engine as the recommendations — and
          explained.
        </p>
      </header>

      <form
        className="mx-auto mt-8 max-w-2xl space-y-6"
        onSubmit={(event) => {
          event.preventDefault()
          build.mutate()
        }}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium">Primary language</span>
            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              className="input"
            >
              <option value="">No preference</option>
              {technologies.map((tag) => (
                <option key={tag.slug} value={tag.slug}>
                  {tag.name}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm font-medium">IDE / editor</span>
            <select value={ide} onChange={(event) => setIde(event.target.value)} className="input">
              <option value="">No preference</option>
              {platforms.map((tag) => (
                <option key={tag.slug} value={tag.slug}>
                  {tag.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <fieldset>
          <legend className="mb-1.5 text-sm font-medium">
            Frameworks <span className="font-normal text-faint">(optional)</span>
          </legend>
          <div className="flex flex-wrap gap-1.5">
            {technologies.slice(0, 20).map((tag) => (
              <Chip
                key={tag.slug}
                label={tag.name}
                active={frameworks.includes(tag.slug)}
                onClick={() =>
                  setFrameworks((current) =>
                    current.includes(tag.slug)
                      ? current.filter((item) => item !== tag.slug)
                      : [...current, tag.slug],
                  )
                }
              />
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="mb-1.5 text-sm font-medium">Goals</legend>
          <div className="flex flex-wrap gap-1.5">
            {GOALS.map((goal) => (
              <Chip
                key={goal}
                label={goal}
                active={goals.includes(goal)}
                onClick={() =>
                  setGoals((current) =>
                    current.includes(goal)
                      ? current.filter((item) => item !== goal)
                      : [...current, goal],
                  )
                }
              />
            ))}
          </div>
        </fieldset>

        {stackAreas.length ? (
          <fieldset>
            <legend className="mb-1.5 text-sm font-medium">
              Areas to include{' '}
              <span className="font-normal text-faint">(leave empty for all)</span>
            </legend>
            <div className="flex flex-wrap gap-1.5">
              {stackAreas.map((area) => (
                <Chip
                  key={area.slug}
                  label={area.area}
                  active={areas.includes(area.slug)}
                  onClick={() =>
                    setAreas((current) =>
                      current.includes(area.slug)
                        ? current.filter((item) => item !== area.slug)
                        : [...current, area.slug],
                    )
                  }
                />
              ))}
            </div>
          </fieldset>
        ) : null}

        <fieldset>
          <legend className="mb-1.5 text-sm font-medium">Budget</legend>
          <div className="flex flex-wrap gap-1.5">
            {BUDGETS.map((option) => (
              <Chip
                key={option.value}
                label={option.label}
                active={budget === option.value}
                onClick={() => setBudget(option.value)}
              />
            ))}
          </div>
        </fieldset>

        <button type="submit" className="btn-primary w-full py-2.5">
          <StackIcon /> Build my stack
        </button>
      </form>

      <div className="mt-10">
        {build.isPending ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-48 w-full rounded-xl" />
            ))}
          </div>
        ) : null}
        {build.error ? <ErrorState error={build.error} onRetry={() => build.mutate()} /> : null}
        {result && !build.isPending ? <StackResult result={result} /> : null}
      </div>
    </div>
  )
}

function StackResult({ result }: { result: StackResponse }) {
  if (!result.slots.length) {
    return (
      <EmptyState
        title="No stack could be assembled with those constraints"
        description="Try widening the budget or removing a technology filter."
        action={
          <Link to="/tools" className="btn-secondary">
            Browse tools instead
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-8">
      <section className="card p-5">
        <h2 className="section-title">Your AI developer stack</h2>
        <p className="mt-2 text-sm text-muted">{result.summary}</p>
        {result.explanation.length ? (
          <ul className="mt-3 space-y-1.5">
            {result.explanation.map((line) => (
              <li key={line} className="flex items-start gap-2 text-sm text-muted">
                <span className="text-positive">✓</span>
                {line}
              </li>
            ))}
          </ul>
        ) : null}
        {result.unmatched_areas.length ? (
          <p className="mt-3 text-2xs text-caution">
            Nothing matched for: {result.unmatched_areas.join(', ')}. Widening the budget usually
            fills these.
          </p>
        ) : null}
      </section>

      {result.slots.map((slot) => (
        <section key={slot.slug}>
          <div className="mb-3">
            <h3 className="text-base font-semibold">{slot.area}</h3>
            <p className="text-2xs text-faint">{slot.description}</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {slot.picks.map((pick, index) => (
              <ToolCard
                key={pick.tool.slug}
                tool={pick.tool}
                highlight={index === 0 ? `Top pick · ${pick.score}%` : `${pick.score}% match`}
                reasons={pick.reasons}
                compact
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}

function Chip({
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
        'badge px-2 py-1 text-xs capitalize transition-colors',
        active ? 'border-accent bg-accent/10 text-accent' : 'text-muted hover:text-ink',
      )}
    >
      {label}
    </button>
  )
}
