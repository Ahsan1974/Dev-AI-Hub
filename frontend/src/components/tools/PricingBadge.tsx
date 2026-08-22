import type { PricingStatusInfo } from '@/types/api'
import { cx, pricingTone } from '@/utils/format'

export function PricingBadge({
  pricing,
  className,
}: {
  pricing: PricingStatusInfo
  className?: string
}) {
  return (
    <span
      className={cx('badge uppercase', pricingTone(pricing.value), className)}
      title={pricing.description}
    >
      {pricing.label}
    </span>
  )
}

export function VerifiedBadge({ label }: { label: string | null }) {
  if (!label) {
    return (
      <span className="badge text-faint" title="We have not verified this record yet.">
        Unverified
      </span>
    )
  }
  return (
    <span className="badge text-muted" title={`Pricing and free access verified in ${label}`}>
      Verified {label}
    </span>
  )
}
