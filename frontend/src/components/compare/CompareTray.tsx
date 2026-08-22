import { useQuery } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import { comparePath } from '@/utils/format'
import { useLocalCollections, MAX_COMPARE } from '@/hooks/useLocalCollections'
import { CrossIcon, ScaleIcon } from '@/components/ui/Icons'

/** Floating tray that follows the user until they compare or clear the shortlist. */
export function CompareTray() {
  const { compare, removeFromCompare, clearCompare } = useLocalCollections()
  const navigate = useNavigate()
  const location = useLocation()

  const { data } = useQuery({
    queryKey: ['resolve-tools', compare],
    queryFn: () => api.resolveTools(compare),
    enabled: compare.length > 0,
    staleTime: 5 * 60 * 1000,
  })

  const onComparePage = location.pathname.startsWith('/compare')
  if (!compare.length || onComparePage) return null

  const names = new Map((data ?? []).map((tool) => [tool.slug, tool.name]))

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-0 z-40 px-4 pb-4">
      <div className="pointer-events-auto mx-auto flex w-full max-w-3xl flex-wrap items-center gap-2 rounded-xl border border-line bg-surface/95 p-2.5 shadow-lg backdrop-blur animate-fade-up">
        <span className="ml-1 hidden items-center gap-1.5 text-2xs font-semibold uppercase tracking-wider text-faint sm:flex">
          <ScaleIcon /> Compare
        </span>
        <ul className="flex flex-1 flex-wrap items-center gap-1.5">
          {compare.map((slug) => (
            <li key={slug}>
              <span className="badge gap-1 bg-raised py-1 text-xs">
                {names.get(slug) ?? slug}
                <button
                  type="button"
                  onClick={() => removeFromCompare(slug)}
                  aria-label={`Remove ${names.get(slug) ?? slug} from comparison`}
                  className="text-faint hover:text-ink"
                >
                  <CrossIcon />
                </button>
              </span>
            </li>
          ))}
        </ul>
        <span className="text-2xs text-faint">
          {compare.length}/{MAX_COMPARE}
        </span>
        <button type="button" onClick={clearCompare} className="btn-ghost px-2 py-1 text-xs">
          Clear
        </button>
        <button
          type="button"
          className="btn-primary px-3 py-1.5 text-xs"
          disabled={compare.length < 2}
          title={compare.length < 2 ? 'Pick at least two tools' : undefined}
          onClick={() => navigate(comparePath(compare))}
        >
          Compare
        </button>
      </div>
    </div>
  )
}
