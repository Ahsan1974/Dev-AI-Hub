import { useEffect, useId, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { SearchIcon } from '@/components/ui/Icons'
import { useDebounced } from '@/hooks/useDebounced'
import { api } from '@/services/api'
import type { SuggestItem } from '@/types/api'
import { cx } from '@/utils/format'

type Props = {
  value: string
  onChange: (value: string) => void
  onSubmit: (query: string) => void
  placeholder?: string
  inputClassName?: string
  autoFocus?: boolean
  size?: 'sm' | 'lg'
}

function typeLabel(type: SuggestItem['type']) {
  if (type === 'tool') return 'Tool'
  if (type === 'category') return 'Category'
  return 'Search'
}

export function SearchSuggest({
  value,
  onChange,
  onSubmit,
  placeholder = 'Search tools...',
  inputClassName,
  autoFocus,
  size = 'sm',
}: Props) {
  const navigate = useNavigate()
  const listId = useId()
  const rootRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(-1)
  const debounced = useDebounced(value.trim(), 200)

  const suggestions = useQuery({
    queryKey: ['search-suggest', debounced],
    queryFn: () => api.suggest(debounced, 8),
    enabled: debounced.length >= 1,
  })

  const items = suggestions.data?.data ?? []

  useEffect(() => {
    setActive(-1)
    setOpen(debounced.length >= 1 && items.length > 0)
  }, [debounced, items.length])

  useEffect(() => {
    const onDoc = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const choose = (item: SuggestItem) => {
    setOpen(false)
    if (item.type === 'tool' && item.slug) {
      navigate(`/tools/${item.slug}`)
      return
    }
    if (item.type === 'category' && item.slug) {
      navigate(`/category/${item.slug}`)
      return
    }
    const query = (item.query || item.label || value).trim()
    onChange(query)
    onSubmit(query)
  }

  const submit = (event: React.FormEvent) => {
    event.preventDefault()
    if (open && active >= 0 && items[active]) {
      choose(items[active])
      return
    }
    setOpen(false)
    onSubmit(value)
  }

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (!open || !items.length) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActive((index) => (index + 1) % items.length)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActive((index) => (index <= 0 ? items.length - 1 : index - 1))
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div ref={rootRef} className="relative w-full">
      <form onSubmit={submit} className="relative">
        <SearchIcon
          className={cx(
            'pointer-events-none absolute top-1/2 -translate-y-1/2 text-faint',
            size === 'lg' ? 'left-4 text-lg' : 'left-3 text-sm',
          )}
        />
        <input
          type="search"
          value={value}
          autoFocus={autoFocus}
          onChange={(event) => {
            onChange(event.target.value)
            setOpen(true)
          }}
          onFocus={() => {
            if (items.length) setOpen(true)
          }}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          aria-label="Search tools"
          aria-autocomplete="list"
          aria-controls={listId}
          aria-expanded={open}
          className={cx(
            size === 'lg'
              ? 'input h-14 rounded-xl pl-12 pr-28 text-base shadow-sm'
              : 'input pl-9',
            inputClassName,
          )}
        />
        {size === 'lg' ? (
          <button
            type="submit"
            className="btn-primary absolute right-2 top-1/2 h-10 -translate-y-1/2 px-4"
          >
            Search
          </button>
        ) : null}
      </form>

      {open && items.length ? (
        <ul
          id={listId}
          role="listbox"
          className="absolute z-50 mt-1 max-h-80 w-full overflow-auto rounded-xl border border-line bg-canvas py-1 shadow-lg"
        >
          {items.map((item, index) => (
            <li
              key={`${item.type}-${item.slug ?? item.label}-${index}`}
              role="option"
              aria-selected={index === active}
            >
              <button
                type="button"
                className={cx(
                  'flex w-full items-start gap-3 px-3 py-2 text-left transition-colors',
                  index === active ? 'bg-raised' : 'hover:bg-raised/70',
                )}
                onMouseEnter={() => setActive(index)}
                onClick={() => choose(item)}
              >
                <span className="mt-0.5 rounded bg-raised px-1.5 py-0.5 text-2xs font-medium uppercase tracking-wide text-faint">
                  {typeLabel(item.type)}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-ink">{item.label}</span>
                  {item.subtitle ? (
                    <span className="block truncate text-xs text-muted">{item.subtitle}</span>
                  ) : null}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
