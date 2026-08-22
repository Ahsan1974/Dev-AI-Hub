import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '@/services/client'
import { cx } from '@/utils/format'
import { InfoIcon, WarnIcon } from './Icons'

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx('skeleton', className)} />
}

export function ToolCardSkeleton() {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-5 w-20 rounded-md" />
        <Skeleton className="h-5 w-24 rounded-md" />
      </div>
      <div className="mt-5 flex gap-2">
        <Skeleton className="h-9 flex-1 rounded-lg" />
        <Skeleton className="h-9 w-28 rounded-lg" />
      </div>
    </div>
  )
}

export function ToolGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: count }).map((_, index) => (
        <ToolCardSkeleton key={index} />
      ))}
    </div>
  )
}

interface EmptyStateProps {
  title: string
  description?: ReactNode
  action?: ReactNode
  icon?: ReactNode
}

export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-12 text-center">
      <div className="grid h-10 w-10 place-items-center rounded-full bg-raised text-muted">
        {icon ?? <InfoIcon className="text-base" />}
      </div>
      <div>
        <p className="font-medium">{title}</p>
        {description ? <p className="mt-1 max-w-md text-sm text-muted">{description}</p> : null}
      </div>
      {action}
    </div>
  )
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const apiError = error instanceof ApiError ? error : null
  const isOffline = apiError?.code === 'NETWORK_ERROR'

  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-12 text-center">
      <div className="grid h-10 w-10 place-items-center rounded-full bg-negative/10 text-negative">
        <WarnIcon className="text-base" />
      </div>
      <div>
        <p className="font-medium">
          {isOffline ? 'The API is not responding' : 'Something went wrong'}
        </p>
        <p className="mt-1 max-w-md text-sm text-muted">
          {apiError?.message ?? 'An unexpected error occurred. Please try again.'}
        </p>
        {isOffline ? (
          <p className="mt-2 font-mono text-2xs text-faint">
            uvicorn app.main:app --reload --port 8000
          </p>
        ) : null}
      </div>
      <div className="flex gap-2">
        {onRetry ? (
          <button type="button" className="btn-secondary" onClick={onRetry}>
            Try again
          </button>
        ) : null}
        <Link to="/" className="btn-ghost">
          Back to home
        </Link>
      </div>
    </div>
  )
}

export function SectionHeader({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: ReactNode
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="section-title">{title}</h2>
        {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
      </div>
      {action}
    </div>
  )
}
