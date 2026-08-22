import type { FreeAccessLine } from '@/types/api'
import { cx } from '@/utils/format'
import { CheckIcon, InfoIcon, WarnIcon } from '@/components/ui/Icons'

const TONE = {
  ok: { icon: CheckIcon, className: 'text-positive' },
  warn: { icon: WarnIcon, className: 'text-caution' },
  info: { icon: InfoIcon, className: 'text-faint' },
} as const

export function FreeAccessList({
  lines,
  className,
  dense = false,
}: {
  lines: FreeAccessLine[]
  className?: string
  dense?: boolean
}) {
  if (!lines.length) return null

  return (
    <ul className={cx('space-y-1', className)}>
      {lines.map((line, index) => {
        const tone = TONE[line.kind]
        const Icon = tone.icon
        return (
          <li key={`${line.kind}-${index}`} className="flex items-start gap-1.5">
            <Icon className={cx('mt-0.5 shrink-0 text-xs', tone.className)} />
            <span className={cx(dense ? 'text-2xs' : 'text-xs', 'text-muted')}>{line.text}</span>
          </li>
        )
      })}
    </ul>
  )
}
