import { Link } from 'react-router-dom'

const LINKS = [
  {
    title: 'Discover',
    items: [
      { to: '/tools', label: 'Browse all tools' },
      { to: '/free-tools', label: 'Free tools' },
      { to: '/free-ai-coding-tools', label: 'Free AI coding tools' },
      { to: '/free-ai-image-tools', label: 'Free AI image tools' },
      { to: '/free-ai-video-tools', label: 'Free AI video tools' },
    ],
  },
  {
    title: 'Decide',
    items: [
      { to: '/what-do-i-need', label: 'What do I need?' },
      { to: '/build-my-stack', label: 'Build my stack' },
      { to: '/compare', label: 'Compare tools' },
      { to: '/collections', label: 'Curated collections' },
    ],
  },
  {
    title: 'Yours',
    items: [
      { to: '/favorites', label: 'Favorites' },
      { to: '/favorites#recent', label: 'Recently viewed' },
    ],
  },
]

export function Footer() {
  return (
    <footer className="mt-16 border-t border-line bg-surface">
      <div className="container-page grid gap-8 py-10 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <p className="font-semibold tracking-tight">DevAI Hub</p>
          <p className="mt-2 max-w-xs text-sm text-muted">
            Discover the right AI tools for every developer task. Free-first, with the free-access
            limits spelled out and every price traced to the provider's own pricing page.
          </p>
        </div>
        {LINKS.map((group) => (
          <div key={group.title}>
            <p className="text-2xs font-semibold uppercase tracking-wider text-faint">
              {group.title}
            </p>
            <ul className="mt-3 space-y-2">
              {group.items.map((item) => (
                <li key={item.to}>
                  <Link to={item.to} className="text-sm text-muted hover:text-ink">
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-line">
        <div className="container-page flex flex-wrap items-center justify-between gap-2 py-4 text-2xs text-faint">
          <p>
            Pricing and free-tier data changes often. Always confirm on the provider's official
            pricing page before you commit.
          </p>
          <a href="/docs" className="hover:text-ink">
            API documentation
          </a>
        </div>
      </div>
    </footer>
  )
}
