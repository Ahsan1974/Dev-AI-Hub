import type { PricingStatus, ToolSummary } from '@/types/api'

export function cx(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(' ')
}

const MONTH_YEAR = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' })
const FULL_DATE = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
})

export function formatMonthYear(value: string | null | undefined): string | null {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : MONTH_YEAR.format(date)
}

export function formatDate(value: string | null | undefined): string | null {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : FULL_DATE.format(date)
}

export function formatPrice(price: number | null, currency = 'USD'): string {
  if (price === null || price === undefined) return 'Not published'
  if (price === 0) return '$0'
  const symbol = currency === 'USD' ? '$' : `${currency} `
  const rounded = Number.isInteger(price) ? price.toString() : price.toFixed(2)
  return `${symbol}${rounded}`
}

export function formatCount(value: number, singular: string, plural = `${singular}s`): string {
  return `${value.toLocaleString()} ${value === 1 ? singular : plural}`
}

/** Tailwind classes for a pricing badge. Free-ish states read as positive. */
export function pricingTone(status: PricingStatus | string): string {
  switch (status) {
    case 'FREE_FOREVER':
    case 'OPEN_SOURCE':
      return 'border-positive/40 bg-positive/10 text-positive'
    case 'FREE_TIER':
    case 'FREE_CREDITS':
      return 'border-accent/40 bg-accent/10 text-accent'
    case 'BYOK':
      return 'border-line bg-raised text-muted'
    case 'FREE_TRIAL':
      return 'border-caution/40 bg-caution/10 text-caution'
    default:
      return 'border-line bg-raised text-muted'
  }
}

/** Short, honest capability chips shown on cards. */
export function capabilityChips(tool: ToolSummary): string[] {
  const chips: string[] = []
  if (tool.flags.is_open_source) chips.push('Open source')
  if (tool.flags.has_agent) chips.push('Agent')
  if (tool.flags.has_api) chips.push(tool.flags.has_free_api ? 'Free API' : 'API')
  if (tool.flags.has_mcp) chips.push('MCP')
  if (tool.flags.has_local_model) chips.push('Local models')
  if (tool.flags.self_hostable && !tool.flags.is_open_source) chips.push('Self-host')
  return chips
}

export function toolPath(slug: string): string {
  return `/tools/${slug}`
}

export function comparePath(slugs: string[]): string {
  return slugs.length >= 2 ? `/compare/${slugs.join('-vs-')}` : '/compare'
}

export function parseComparePath(param: string | undefined): string[] {
  if (!param) return []
  return param
    .split('-vs-')
    .map((slug) => slug.trim().toLowerCase())
    .filter(Boolean)
}

export function pluralizeTools(count: number): string {
  return formatCount(count, 'tool')
}
