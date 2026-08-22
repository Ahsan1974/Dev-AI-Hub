import { useState } from 'react'
import { cx } from '@/utils/format'

interface ToolLogoProps {
  name: string
  initials: string
  logoUrl?: string | null
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const SIZES = {
  sm: 'h-8 w-8 text-2xs',
  md: 'h-10 w-10 text-xs',
  lg: 'h-14 w-14 text-base',
} as const

/**
 * Renders the official logo when it loads and an initials avatar otherwise, so
 * a dead image URL never leaves a hole in a card.
 */
export function ToolLogo({ name, initials, logoUrl, size = 'md', className }: ToolLogoProps) {
  const [failed, setFailed] = useState(false)
  const showImage = Boolean(logoUrl) && !failed

  return (
    <div
      className={cx(
        'grid shrink-0 place-items-center overflow-hidden rounded-lg border border-line bg-raised font-semibold tracking-wide text-muted',
        SIZES[size],
        className,
      )}
    >
      {showImage ? (
        <img
          src={logoUrl as string}
          alt=""
          loading="lazy"
          decoding="async"
          className="h-full w-full object-contain p-1.5"
          onError={() => setFailed(true)}
        />
      ) : (
        <span aria-hidden="true">{initials || name.slice(0, 2).toUpperCase()}</span>
      )}
    </div>
  )
}
