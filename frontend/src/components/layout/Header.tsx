import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { cx } from '@/utils/format'
import { useTheme } from '@/hooks/useTheme'
import { useLocalCollections } from '@/hooks/useLocalCollections'
import { SearchSuggest } from '@/components/search/SearchSuggest'
import {
  HeartIcon,
  MenuIcon,
  MoonIcon,
  SunIcon,
  CrossIcon,
} from '@/components/ui/Icons'

const NAV = [
  { to: '/tools', label: 'Browse' },
  { to: '/free-tools', label: 'Free tools' },
  { to: '/collections', label: 'Collections' },
  { to: '/what-do-i-need', label: 'What do I need?' },
  { to: '/build-my-stack', label: 'Build my stack' },
  { to: '/compare', label: 'Compare' },
]

export function Header() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { theme, toggleTheme } = useTheme()
  const { favorites } = useLocalCollections()
  const [menuOpen, setMenuOpen] = useState(false)
  const [term, setTerm] = useState('')

  const onSearchPage = location.pathname === '/search'

  useEffect(() => {
    setTerm(onSearchPage ? (searchParams.get('q') ?? '') : '')
  }, [onSearchPage, searchParams])

  useEffect(() => setMenuOpen(false), [location.pathname])

  const goSearch = (query: string) => {
    const trimmed = query.trim()
    navigate(trimmed ? `/search?q=${encodeURIComponent(trimmed)}` : '/search')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-canvas/85 backdrop-blur">
      <div className="container-page flex h-14 items-center gap-3">
        <Link to="/" className="flex shrink-0 items-center gap-2 font-semibold tracking-tight">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-accent font-mono text-sm text-accent-ink">
            {'</>'.slice(0, 2)}
          </span>
          <span>DevAI Hub</span>
        </Link>

        <div className="relative ml-2 hidden max-w-sm flex-1 lg:block">
          <SearchSuggest
            value={term}
            onChange={setTerm}
            onSubmit={goSearch}
            placeholder="Search tools..."
          />
        </div>

        <nav className="ml-auto hidden items-center gap-1 lg:flex">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cx(
                  'rounded-lg px-2.5 py-1.5 text-sm transition-colors',
                  isActive ? 'bg-raised text-ink' : 'text-muted hover:text-ink',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-1 lg:ml-2">
          <Link
            to="/favorites"
            className="relative rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-ink"
            aria-label={`Favorites (${favorites.length} saved)`}
          >
            <HeartIcon className="text-base" filled={favorites.length > 0} />
            {favorites.length ? (
              <span className="absolute -right-0.5 -top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-accent px-1 text-2xs font-semibold text-accent-ink">
                {favorites.length}
              </span>
            ) : null}
          </Link>
          <button
            type="button"
            onClick={toggleTheme}
            className="rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-ink"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <SunIcon className="text-base" /> : <MoonIcon className="text-base" />}
          </button>
          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            className="rounded-lg p-2 text-muted transition-colors hover:bg-raised hover:text-ink lg:hidden"
            aria-expanded={menuOpen}
            aria-label="Toggle navigation menu"
          >
            {menuOpen ? <CrossIcon className="text-base" /> : <MenuIcon className="text-base" />}
          </button>
        </div>
      </div>

      {menuOpen ? (
        <div className="border-t border-line bg-surface lg:hidden">
          <div className="container-page space-y-3 py-3">
            <SearchSuggest
              value={term}
              onChange={setTerm}
              onSubmit={(query) => {
                goSearch(query)
                setMenuOpen(false)
              }}
              placeholder="Search tools..."
            />
            <nav className="flex flex-col gap-1">
              {NAV.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cx(
                      'rounded-lg px-3 py-2 text-sm',
                      isActive ? 'bg-raised text-ink' : 'text-muted',
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      ) : null}
    </header>
  )
}
