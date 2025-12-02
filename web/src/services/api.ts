import axios from 'axios';
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  BatchAnalyzeRequest,
  BatchAnalyzeResponse,
  ScoreRequest,
  ScoreResponse,
  SourceDetailed,
  SourceListResponse,
  CounternarrativeResponse,
  StatsResponse,
  SourceFilters,
  ContentAnalysisRequest,
  ContentAnalysisResponse,
  UsageStatsResponse,
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Analyze Endpoints
// ============================================================================

/**
 * Analyze a single article URL
 */
export async function analyzeUrl(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await api.post<AnalyzeResponse>('/analyze', request);
  return response.data;
}

/**
 * Analyze multiple URLs in batch
 */
export async function analyzeUrlBatch(request: BatchAnalyzeRequest): Promise<BatchAnalyzeResponse> {
  const response = await api.post<BatchAnalyzeResponse>('/analyze/batch', request);
  return response.data;
}

// ============================================================================
// Sources Endpoints
// ============================================================================

/**
 * Get detailed information about a source by domain
 */
export async function getSource(domain: string): Promise<SourceDetailed> {
  const response = await api.get<SourceDetailed>(`/sources/${encodeURIComponent(domain)}`);
  return response.data;
}

/**
 * List sources with optional filters
 */
export async function listSources(filters?: SourceFilters): Promise<SourceListResponse> {
  const params = new URLSearchParams();

  if (filters) {
    if (filters.lean !== undefined) params.set('lean', String(filters.lean));
    if (filters.min_credibility !== undefined) params.set('min_credibility', String(filters.min_credibility));
    if (filters.source_type) params.set('source_type', filters.source_type);
    if (filters.limit !== undefined) params.set('limit', String(filters.limit));
    if (filters.offset !== undefined) params.set('offset', String(filters.offset));
  }

  const response = await api.get<SourceListResponse>('/sources', { params });
  return response.data;
}

/**
 * Bulk lookup multiple domains
 */
export async function lookupDomains(domains: string[]): Promise<SourceListResponse> {
  const params = new URLSearchParams();
  params.set('domains', domains.join(','));

  const response = await api.get<SourceListResponse>('/sources', { params });
  return response.data;
}

/**
 * Get counternarratives for a source
 */
export async function getCounternarratives(
  domain: string,
  options?: {
    min_credibility?: number;
    limit?: number;
    preferred_leans?: number[];
  }
): Promise<CounternarrativeResponse> {
  const params = new URLSearchParams();

  if (options) {
    if (options.min_credibility !== undefined) params.set('min_credibility', String(options.min_credibility));
    if (options.limit !== undefined) params.set('limit', String(options.limit));
    if (options.preferred_leans) params.set('preferred_leans', options.preferred_leans.join(','));
  }

  const response = await api.get<CounternarrativeResponse>(
    `/sources/${encodeURIComponent(domain)}/counternarratives`,
    { params }
  );
  return response.data;
}

/**
 * Score a source for evidence quality
 */
export async function scoreSource(request: ScoreRequest): Promise<ScoreResponse> {
  const response = await api.post<ScoreResponse>('/sources/score', request);
  return response.data;
}

/**
 * Get database statistics
 */
export async function getStats(): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>('/sources/stats/overview');
  return response.data;
}

// ============================================================================
// Content Analysis Endpoints
// ============================================================================

/**
 * Analyze article content for quality, bias, and reliability
 */
export async function analyzeContent(request: ContentAnalysisRequest): Promise<ContentAnalysisResponse> {
  const response = await api.post<ContentAnalysisResponse>('/content/analyze', request);
  return response.data;
}

// ============================================================================
// Usage Stats
// ============================================================================

/**
 * Get API usage statistics and cost breakdown
 */
export async function getUsageStats(days: number = 30): Promise<UsageStatsResponse> {
  const response = await api.get<UsageStatsResponse>('/usage/stats', {
    params: { days }
  });
  return response.data;
}

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health status
 */
export async function healthCheck(): Promise<{ status: string; version: string; database: string }> {
  const response = await api.get('/health');
  return response.data;
}

export default api;
