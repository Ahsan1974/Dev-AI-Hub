import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { CrossIcon } from '@/components/ui/Icons'

/** Mobile presentation of the filter sidebar. */
export function FilterDrawer({
  open,
  onClose,
  children,
}: {
  open: boolean
  onClose: () => void
  children: ReactNode
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Filters">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="absolute inset-y-0 right-0 flex w-full max-w-sm flex-col bg-canvas shadow-xl">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <p className="font-medium">Filters</p>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted hover:bg-raised hover:text-ink"
            aria-label="Close filters"
          >
            <CrossIcon className="text-base" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">{children}</div>
        <div className="border-t border-line p-4">
          <button type="button" className="btn-primary w-full" onClick={onClose}>
            Show results
          </button>
        </div>
      </div>
    </div>
  )
}
