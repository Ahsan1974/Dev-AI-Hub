import { Link } from 'react-router-dom'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'

export function NotFoundPage({ title = 'Page not found' }: { title?: string }) {
  useDocumentMeta({ title, description: 'The page you were looking for does not exist.' })

  return (
    <div className="container-page flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="font-mono text-sm text-faint">404</p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">{title}</h1>
      <p className="mt-2 max-w-md text-sm text-muted">
        The link may be out of date. Search the catalogue instead — there is a good chance the tool
        is here under a different slug.
      </p>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <Link to="/" className="btn-primary">
          Back to home
        </Link>
        <Link to="/search" className="btn-secondary">
          Search tools
        </Link>
        <Link to="/free-tools" className="btn-ghost">
          Free tools
        </Link>
      </div>
    </div>
  )
}
