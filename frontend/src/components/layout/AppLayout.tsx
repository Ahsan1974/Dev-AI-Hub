import { useEffect } from 'react'
import { Outlet, ScrollRestoration, useLocation } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'
import { CompareTray } from '@/components/compare/CompareTray'

export function AppLayout() {
  const { pathname, hash } = useLocation()

  // Route changes should land at the top unless the URL targets an anchor.
  useEffect(() => {
    if (!hash) window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior })
  }, [pathname, hash])

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-accent focus:px-3 focus:py-2 focus:text-accent-ink"
      >
        Skip to content
      </a>
      <Header />
      <main id="main" className="flex-1 pb-24">
        <Outlet />
      </main>
      <Footer />
      <CompareTray />
      <ScrollRestoration />
    </div>
  )
}
