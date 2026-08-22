import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '@/services/api'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { ToolCard } from '@/components/tools/ToolCard'
import { EmptyState, ErrorState, ToolGridSkeleton } from '@/components/ui/States'
import { SparkIcon } from '@/components/ui/Icons'
import { cx } from '@/utils/format'
import type { Budget, RecommendationResponse } from '@/types/api'

const BUDGETS: Array<{ value: Budget; label: string; hint: string }> = [
  { value: 'free_only', label: 'Free only', hint: 'Only tools with real free access' },
  { value: 'mostly_free', label: 'Mostly free', hint: 'Prefer free, allow paid if it fits' },
  { value: 'any', label: 'Any price', hint: 'Rank purely on fit' },
]

const EXAMPLES = [
  'I need a free AI tool to generate Java unit tests',
  'Open source coding agent I can run locally',
  'Free image generator with no watermark',
  'Something to review my pull requests automatically',
  'Run an LLM on my own machine',
  'Turn my API into readable documentation',
]

export function WhatDoINeedPage() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') ?? '')
  const [budget, setBudget] = useState<Budget>('mostly_free')
  const [technologies, setTechnologies] = useState<string[]>([])
  const [result, setResult] = useState<RecommendationResponse | null>(null)

  useDocumentMeta({
    title: 'What do I need?',
    description:
      'Describe your task in your own words and get explainable AI tool recommendations, scored on category, keyword, technology, feature and pricing fit.',
  })

  const { data: filters } = useQuery({
    queryKey: ['filters'],
    queryFn: api.filters,
    staleTime: 10 * 60 * 1000,
  })

  const recommend = useMutation({
    mutationFn: () =>
      api.recommend({ query: query.trim(), budget, technologies, limit: 9 }),
    onSuccess: setResult,
  })

  // Deep links from empty search results run immediately.
  useEffect(() => {
    const initial = searchParams.get('q')
    if (initial && initial.trim().length >= 3) recommend.mutate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const topTechnologies = (filters?.technologies ?? []).slice(0, 18)
  const canSubmit = query.trim().length >= 3

  return (
    <div className="container-page py-8">
      <header className="mx-auto max-w-2xl text-center">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">What do you need?</h1>
        <p className="mt-2 text-sm text-muted">
          Describe your task in your own words. Scoring is rule-based and explained on every
          result — no API key, no black box.
        </p>
      </header>

      <form
        className="mx-auto mt-8 max-w-2xl space-y-5"
        onSubmit={(event) => {
          event.preventDefault()
          if (canSubmit) recommend.mutate()
        }}
      >
        <div>
          <label htmlFor="task" className="mb-1.5 block text-sm font-medium">
            Your task
          </label>
          <textarea
            id="task"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            rows={3}
            placeholder="I need an AI tool to..."
            className="input resize-y text-base"
          />
          <div className="mt-2 flex flex-wrap gap-1.5">
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setQuery(example)}
                className="badge px-2 py-1 text-2xs text-muted hover:border-accent/50 hover:text-ink"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <fieldset>
          <legend className="mb-1.5 text-sm font-medium">Budget</legend>
          <div className="grid gap-2 sm:grid-cols-3">
            {BUDGETS.map((option) => (
              <label
                key={option.value}
                className={cx(
                  'card cursor-pointer p-3 transition-colors',
                  budget === option.value ? 'border-accent ring-1 ring-accent/30' : 'hover:bg-raised',
                )}
              >
                <span className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="budget"
                    value={option.value}
                    checked={budget === option.value}
                    onChange={() => setBudget(option.value)}
                    className="accent-accent"
                  />
                  <span className="text-sm font-medium">{option.label}</span>
                </span>
                <span className="mt-1 block pl-6 text-2xs text-faint">{option.hint}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {topTechnologies.length ? (
          <fieldset>
            <legend className="mb-1.5 text-sm font-medium">
              Technology <span className="font-normal text-faint">(optional)</span>
            </legend>
            <div className="flex flex-wrap gap-1.5">
              {topTechnologies.map((tag) => {
                const active = technologies.includes(tag.slug)
                return (
                  <button
                    key={tag.slug}
                    type="button"
                    onClick={() =>
                      setTechnologies((current) =>
                        active
                          ? current.filter((item) => item !== tag.slug)
                          : [...current, tag.slug],
                      )
                    }
                    className={cx(
                      'badge px-2 py-1 text-xs transition-colors',
                      active
                        ? 'border-accent bg-accent/10 text-accent'
                        : 'text-muted hover:text-ink',
                    )}
                  >
                    {tag.name}
                  </button>
                )
              })}
            </div>
          </fieldset>
        ) : null}

        <button type="submit" className="btn-primary w-full py-2.5" disabled={!canSubmit}>
          <SparkIcon /> Find tools
        </button>
      </form>

      <div className="mt-10">
        {recommend.isPending ? <ToolGridSkeleton count={6} /> : null}
        {recommend.error ? (
          <ErrorState error={recommend.error} onRetry={() => recommend.mutate()} />
        ) : null}
        {result && !recommend.isPending ? <Results result={result} /> : null}
      </div>
    </div>
  )
}

function Results({ result }: { result: RecommendationResponse }) {
  if (!result.best_match) {
    return (
      <EmptyState
        title="Nothing in the catalogue matches that yet"
        description="We would rather say so than pad the list with tools that do not fit. Try describing the task differently, or browse by category."
        action={
          <div className="flex gap-2">
            <Link to="/tools" className="btn-secondary">
              Browse all tools
            </Link>
            <Link to="/free-tools" className="btn-ghost">
              Free tools
            </Link>
          </div>
        }
      />
    )
  }

  const { meta } = result

  return (
    <div className="space-y-8">
      <section>
        <h2 className="section-title">Best match</h2>
        <div className="mt-3 grid gap-4 lg:grid-cols-3">
          <ToolCard
            tool={result.best_match.tool}
            highlight={`Best match · ${result.best_match.score}%`}
            reasons={result.best_match.reasons}
          />
          <div className="card p-4 lg:col-span-2">
            <h3 className="text-sm font-semibold">Why it matches</h3>
            <ul className="mt-2 space-y-1.5">
              {result.best_match.reasons.map((reason) => (
                <li key={reason} className="flex items-start gap-2 text-sm text-muted">
                  <span className="text-positive">✓</span>
                  {reason}
                </li>
              ))}
            </ul>
            <div className="mt-4 border-t border-line pt-3">
              <h3 className="text-2xs font-semibold uppercase tracking-wider text-faint">
                How we read your request
              </h3>
              <dl className="mt-2 space-y-1 text-2xs text-muted">
                <Interpretation label="Keywords" values={meta.interpreted_keywords} />
                <Interpretation label="Categories" values={meta.detected_categories} />
                <Interpretation label="Technologies" values={meta.detected_technologies} />
                <Interpretation label="Features" values={meta.detected_features} />
                <div className="flex gap-2">
                  <dt className="w-24 shrink-0 text-faint">Budget</dt>
                  <dd>{meta.budget.replace(/_/g, ' ')}</dd>
                </div>
                <div className="flex gap-2">
                  <dt className="w-24 shrink-0 text-faint">Considered</dt>
                  <dd>{meta.candidates_considered} tools</dd>
                </div>
              </dl>
              <p className="mt-3 text-2xs text-faint">
                Score weights:{' '}
                {Object.entries(meta.scoring_weights)
                  .map(([key, value]) => `${key} ${value}`)
                  .join(' · ')}
                . Only the dimensions your request expresses count toward the percentage.
              </p>
              {meta.notes.map((note) => (
                <p key={note} className="mt-2 text-2xs text-faint">
                  {note}
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>

      {result.other_options.length ? (
        <section>
          <h2 className="section-title">Other good options</h2>
          <div className="mt-3 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {result.other_options.map((option) => (
              <ToolCard
                key={option.tool.slug}
                tool={option.tool}
                highlight={`${option.score}% match`}
                reasons={option.reasons}
              />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}

function Interpretation({ label, values }: { label: string; values: string[] }) {
  if (!values.length) return null
  return (
    <div className="flex gap-2">
      <dt className="w-24 shrink-0 text-faint">{label}</dt>
      <dd className="font-mono">{values.join(', ')}</dd>
    </div>
  )
}
