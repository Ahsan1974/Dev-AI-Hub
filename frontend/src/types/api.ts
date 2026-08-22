/** Mirrors the Pydantic schemas exposed by the FastAPI backend. */

export type PricingStatus =
  | 'FREE_FOREVER'
  | 'FREE_TIER'
  | 'FREE_CREDITS'
  | 'FREE_TRIAL'
  | 'OPEN_SOURCE'
  | 'BYOK'
  | 'PAID_ONLY'

export interface PricingStatusInfo {
  value: PricingStatus | string
  label: string
  description: string
  is_free: boolean
}

export interface FreeAccessLine {
  kind: 'ok' | 'warn' | 'info'
  text: string
}

export interface VerificationInfo {
  last_verified_at: string | null
  source_url: string | null
  note: string | null
  is_verified: boolean
  is_stale: boolean
}

export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  group: string
  icon: string | null
  sort_order: number
}

export interface CategoryWithCount extends Category {
  tool_count: number
  free_tool_count: number
}

export interface Tag {
  id: number
  name: string
  slug: string
  kind: string
}

export interface TagWithCount extends Tag {
  tool_count: number
}

export interface ToolCapabilities {
  is_open_source: boolean
  has_api: boolean
  has_free_api: boolean
  has_mcp: boolean
  has_agent: boolean
  has_local_model: boolean
  self_hostable: boolean
}

export interface ToolSummary {
  id: number
  name: string
  slug: string
  tagline: string
  description: string
  website_url: string
  logo_url: string | null
  initials: string
  pricing_status: PricingStatus | string
  pricing: PricingStatusInfo
  pricing_headline: string
  free_access_headline: string
  free_access_lines: FreeAccessLine[]
  categories: Category[]
  languages: string[]
  features: string[]
  platforms: string[]
  integrations: string[]
  flags: ToolCapabilities
  featured: boolean
  is_verified: boolean
  last_verified_at: string | null
  created_at: string | null
}

export interface PricingPlan {
  id: number
  name: string
  price: number | null
  currency: string
  billing_period: string
  is_free: boolean
  is_trial: boolean
  is_per_seat: boolean
  description: string | null
  features: string[]
}

export interface FreeAccessGrant {
  id: number
  type: string
  amount: number | null
  unit: string | null
  period: string | null
  description: string | null
  restrictions: string[]
  requires_credit_card: boolean | null
  expires: boolean | null
  expires_after_days: number | null
}

export interface QualityComponent {
  key: string
  label: string
  score: number
  max_score: number
}

export interface QualityScore {
  score: number
  max_score: number
  components: QualityComponent[]
}

export interface ToolDetail extends ToolSummary {
  long_description: string | null
  pricing_url: string | null
  docs_url: string | null
  repo_url: string | null
  pricing_summary: string | null
  free_access_summary: string | null
  free_access_grants: FreeAccessGrant[]
  pricing_plans: PricingPlan[]
  capabilities: string[]
  best_for: string[]
  not_ideal_for: string[]
  tags: Tag[]
  requires_credit_card: boolean | null
  free_access_expires: boolean | null
  verification: VerificationInfo
  quality: QualityScore
  updated_at: string | null
}

export interface ToolWithScore {
  tool: ToolSummary
  score: number
  reasons: string[]
  matched_categories: string[]
  matched_technologies: string[]
  matched_features: string[]
}

export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface Page<T> {
  data: T[]
  pagination: PaginationMeta
}

export interface DataResponse<T> {
  data: T
}

export interface FacetValue {
  value: string
  label: string
  count: number
}

export interface SearchFacets {
  pricing: FacetValue[]
  categories: FacetValue[]
  technologies: FacetValue[]
  features: FacetValue[]
  platforms: FacetValue[]
}

export interface SearchMeta {
  query: string | null
  interpreted_keywords: string[]
  detected_free_intent: boolean
  engine: 'postgres_fts' | 'portable_like'
  took_ms: number
  suggestions: string[]
}

export interface SearchResponse {
  data: ToolSummary[]
  pagination: PaginationMeta
  meta: SearchMeta
  facets: SearchFacets | null
}

export interface SuggestItem {
  type: 'tool' | 'category' | 'query'
  label: string
  subtitle: string | null
  slug: string | null
  query: string | null
}

export interface SuggestResponse {
  data: SuggestItem[]
}

export interface FilterOptions {
  pricing: FacetValue[]
  categories: CategoryWithCount[]
  technologies: TagWithCount[]
  features: TagWithCount[]
  platforms: TagWithCount[]
  integrations: TagWithCount[]
  sorts: FacetValue[]
}

export interface Workflow {
  slug: string
  label: string
  description: string
  icon: string
  query: string
  categories: string[]
}

export interface Collection {
  id: number
  name: string
  slug: string
  description: string | null
  icon: string | null
  is_featured: boolean
  tool_count: number
}

export interface CollectionDetail extends Collection {
  tools: ToolSummary[]
}

export interface PlatformStats {
  tools: number
  free_tools: number
  categories: number
  collections: number
  verified_tools: number
}

export interface HomeResponse {
  stats: PlatformStats
  featured_free: ToolSummary[]
  popular_categories: CategoryWithCount[]
  recently_added: ToolSummary[]
  developer_favorites: ToolSummary[]
  favorites_available: boolean
  workflows: Workflow[]
  collections: Collection[]
  popular_searches: string[]
}

export interface ToolSection {
  slug: string
  title: string
  description: string
  tools: ToolSummary[]
  total: number
}

export interface FreeToolsResponse {
  sections: ToolSection[]
  categories: CategoryWithCount[]
  active_category: string | null
  total_free_tools: number
}

export type Budget = 'free_only' | 'mostly_free' | 'any'

export interface RecommendationRequest {
  query: string
  budget: Budget
  technologies?: string[]
  categories?: string[]
  limit?: number
}

export interface RecommendationMeta {
  strategy: 'rule_based_scoring' | 'llm_reranked'
  interpreted_keywords: string[]
  detected_categories: string[]
  detected_technologies: string[]
  detected_features: string[]
  budget: string
  candidates_considered: number
  scoring_weights: Record<string, number>
  notes: string[]
}

export interface RecommendationResponse {
  best_match: ToolWithScore | null
  other_options: ToolWithScore[]
  meta: RecommendationMeta
}

export interface StackRequest {
  primary_language?: string | null
  frameworks?: string[]
  ide?: string | null
  goals?: string[]
  budget: Budget
  include_areas?: string[]
}

export interface StackSlot {
  area: string
  slug: string
  description: string
  picks: ToolWithScore[]
}

export interface StackResponse {
  slots: StackSlot[]
  summary: string
  explanation: string[]
  unmatched_areas: string[]
}

export type CompareCellKind = 'bool' | 'text' | 'list' | 'price' | 'unknown'

export interface CompareCell {
  kind: CompareCellKind
  value: boolean | string | string[] | null
  note: string | null
}

export interface CompareRow {
  key: string
  label: string
  group: string
  cells: CompareCell[]
}

export interface CompareResponse {
  tools: ToolDetail[]
  rows: CompareRow[]
  missing_slugs: string[]
}

export interface StackArea {
  slug: string
  area: string
  description: string
  categories: string[]
  query: string
}

export interface MetaResponse {
  pricing_statuses: PricingStatusInfo[]
  workflows: Workflow[]
  stack_areas: StackArea[]
  popular_searches: string[]
}

export interface ToolPricingResponse {
  tool_slug: string
  pricing_status: string
  pricing_summary: string | null
  plans: PricingPlan[]
  pricing_url: string | null
  last_verified_at: string | null
  verification_source_url: string | null
  disclaimer: string
}
