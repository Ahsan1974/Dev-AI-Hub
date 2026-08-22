import { buildQuery, request, requestData, type QueryValue } from './client'
import type {
  CategoryWithCount,
  CollectionDetail,
  Collection,
  CompareResponse,
  FilterOptions,
  FreeToolsResponse,
  HomeResponse,
  MetaResponse,
  Page,
  RecommendationRequest,
  RecommendationResponse,
  SearchResponse,
  StackRequest,
  StackResponse,
  SuggestResponse,
  ToolDetail,
  ToolSummary,
} from '@/types/api'

/** Query state shared by browse, search, category and free-tools surfaces. */
export interface ToolQuery {
  q?: string
  category?: string[]
  technology?: string[]
  feature?: string[]
  platform?: string[]
  integration?: string[]
  pricing?: string[]
  free_only?: boolean
  open_source?: boolean
  has_api?: boolean
  has_free_api?: boolean
  has_mcp?: boolean
  has_agent?: boolean
  has_local_model?: boolean
  sort?: string
  page?: number
  page_size?: number
}

function toParams(query: ToolQuery): Record<string, QueryValue> {
  const params: Record<string, QueryValue> = {}
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue
    if (typeof value === 'boolean') {
      // Only send booleans when true; `false` means "no opinion" here.
      if (value) params[key] = 'true'
      continue
    }
    params[key] = value as QueryValue
  }
  return params
}

export const api = {
  home: () => requestData<HomeResponse>('/home'),

  meta: () => requestData<MetaResponse>('/meta'),

  tools: (query: ToolQuery = {}) =>
    request<Page<ToolSummary>>(`/tools${buildQuery(toParams(query))}`),

  tool: (slug: string) => requestData<ToolDetail>(`/tools/${encodeURIComponent(slug)}`),

  alternatives: (slug: string, limit = 6) =>
    requestData<ToolSummary[]>(
      `/tools/${encodeURIComponent(slug)}/alternatives${buildQuery({ limit })}`,
    ),

  resolveTools: (slugs: string[]) =>
    slugs.length
      ? requestData<ToolSummary[]>('/tools/resolve', { method: 'POST', body: { slugs } })
      : Promise.resolve([]),

  search: (query: ToolQuery) => request<SearchResponse>(`/search${buildQuery(toParams(query))}`),

  suggest: (q: string, limit = 8) =>
    request<SuggestResponse>(`/search/suggest${buildQuery({ q, limit })}`),

  filters: () => requestData<FilterOptions>('/filters'),

  categories: () => requestData<CategoryWithCount[]>('/categories'),

  category: (slug: string) => requestData<CategoryWithCount>(`/categories/${encodeURIComponent(slug)}`),

  categoryTools: (slug: string, query: ToolQuery = {}) =>
    request<Page<ToolSummary>>(
      `/categories/${encodeURIComponent(slug)}/tools${buildQuery(toParams(query))}`,
    ),

  freeTools: (category?: string | null, limit = 12) =>
    requestData<FreeToolsResponse>(`/free-tools${buildQuery({ category, limit })}`),

  collections: (featured = false) =>
    requestData<Collection[]>(`/collections${buildQuery({ featured: featured ? 'true' : undefined })}`),

  collection: (slug: string) =>
    requestData<CollectionDetail>(`/collections/${encodeURIComponent(slug)}`),

  recommend: (body: RecommendationRequest) =>
    requestData<RecommendationResponse>('/recommendations', { method: 'POST', body }),

  buildStack: (body: StackRequest) =>
    requestData<StackResponse>('/recommendations/stack', { method: 'POST', body }),

  compare: (slugs: string[]) =>
    requestData<CompareResponse>('/compare', { method: 'POST', body: { slugs } }),
}
