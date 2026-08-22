import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SearchSuggest } from '@/components/search/SearchSuggest'

/** Large search entry used on the homepage hero. */
export function SearchHero({ popular }: { popular: string[] }) {
  const [term, setTerm] = useState('')
  const navigate = useNavigate()

  const go = (query: string) => {
    const trimmed = query.trim()
    navigate(trimmed ? `/search?q=${encodeURIComponent(trimmed)}` : '/search')
  }

  return (
    <div className="w-full">
      <SearchSuggest
        value={term}
        onChange={setTerm}
        onSubmit={go}
        placeholder="What do you need help with?"
        size="lg"
      />

      {popular.length ? (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-2xs font-medium uppercase tracking-wider text-faint">
            Popular searches
          </span>
          {popular.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => go(item)}
              className="badge px-2 py-1 text-xs text-muted transition-colors hover:border-accent/50 hover:text-ink"
            >
              {item}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
