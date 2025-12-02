// Source types
export interface Source {
  domain: string;
  name: string;
  political_lean: number | null;
  political_lean_label: string | null;
  newsguard_score: number | null;
  newsguard_rating: string | null;
  source_type: string | null;
  description: string | null;
}

export interface SourceDetailed extends Source {
  ownership_summary: string | null;
  criteria: Record<string, unknown> | null;
  created_at: string | null;
}

export interface SourceWithScore extends Source {
  weighted_score: number | null;
}

// Request types
export interface AnalyzeRequest {
  url: string;
  include_counternarratives?: boolean;
  min_counternarrative_credibility?: number;
  counternarrative_limit?: number;
  preferred_leans?: number[];
}

export interface BatchAnalyzeRequest {
  urls: string[];
  options?: Omit<AnalyzeRequest, 'url'>;
}

export interface ScoreRequest {
  domain: string;
  context?: {
    claim_type?: 'political' | 'economic' | 'foreign_policy' | 'scientific' | 'general';
    evidence_role?: 'support' | 'refute' | 'neutral';
    preferred_credibility?: 'high' | 'medium' | 'any';
  };
}

// Response types
export interface AnalyzeResponse {
  url: string;
  domain: string;
  source: SourceDetailed | null;
  source_found: boolean;
  counternarratives: SourceWithScore[] | null;
  error: string | null;
}

export interface BatchAnalyzeResponse {
  results: AnalyzeResponse[];
  total: number;
  successful: number;
  failed: number;
}

export interface ScoringBreakdown {
  credibility_score: number;
  bias_penalty: number;
  type_bonus: number;
  explanation: string;
}

export interface ScoreResponse {
  source: Source | null;
  weighted_score: number | null;
  scoring_breakdown: ScoringBreakdown | null;
  recommendation: 'strong' | 'acceptable' | 'use_with_caution' | 'not_recommended' | null;
  error: string | null;
}

export interface SourceListResponse {
  sources: Source[];
  total: number;
  limit: number;
  offset: number;
  filters_applied: Record<string, unknown>;
}

export interface CounternarrativeResponse {
  source_domain: string;
  source_name: string | null;
  source_lean: string | null;
  counternarratives: SourceWithScore[];
  total: number;
}

export interface StatsResponse {
  total_sources: number;
  with_newsguard: number;
  with_political_lean: number;
  lean_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
  credibility_tiers: {
    high: number;
    medium: number;
    low: number;
  };
}

// Filter types
export interface SourceFilters {
  lean?: number;
  min_credibility?: number;
  source_type?: string;
  limit?: number;
  offset?: number;
}

// Content Analysis types
export interface ContentAnalysisRequest {
  url: string;
  content?: string;
  model?: string;
}

export interface AnalysisScores {
  inflammatory_language: number;
  unsupported_claims: number;
  emotional_manipulation: number;
  factual_reporting: number;
  overall_quality: number;
  overall_grade: string;
}

export interface UnsupportedClaim {
  claim: string;
  issue: string;
}

export interface ContentAnalysisResponse {
  url: string;
  success: boolean;
  summary: string | null;
  scores: AnalysisScores | null;
  inflammatory_examples: string[];
  inflammatory_explanation: string | null;
  unsupported_claims: UnsupportedClaim[];
  claims_explanation: string | null;
  manipulation_techniques: string[];
  manipulation_explanation: string | null;
  factual_strengths: string[];
  factual_weaknesses: string[];
  detected_bias: string | null;
  bias_indicators: string[];
  bias_explanation: string | null;
  recommendation: string | null;
  word_count: number | null;
  fetch_method: string | null;
  model_used: string | null;
  error: string | null;
}

// Usage Stats types
export interface ApiUsageBreakdown {
  api_name: string;
  calls: number;
  cost: number;
}

export interface ModelUsageBreakdown {
  model_used: string;
  calls: number;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  avg_cost_per_call: number;
}

export interface DailyUsage {
  date: string;
  calls: number;
  input_tokens: number;
  output_tokens: number;
  cost: number;
}

export interface ExpensiveAnalysis {
  url: string;
  model_used: string | null;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  timestamp: string;
}

export interface UsageTotals {
  total_calls: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost: number;
  successful_calls: number;
  failed_calls: number;
}

export interface UsageStatsResponse {
  period_days: number;
  totals: UsageTotals;
  by_api: ApiUsageBreakdown[];
  by_model: ModelUsageBreakdown[];
  daily: DailyUsage[];
  top_expensive: ExpensiveAnalysis[];
}

// Political lean helpers
export const LEAN_LABELS: Record<number, string> = {
  [-2]: 'Left',
  [-1]: 'Lean Left',
  [0]: 'Center',
  [1]: 'Lean Right',
  [2]: 'Right',
};

export const LEAN_COLORS: Record<number, string> = {
  [-2]: 'bg-blue-600',
  [-1]: 'bg-blue-400',
  [0]: 'bg-purple-500',
  [1]: 'bg-red-400',
  [2]: 'bg-red-600',
};

export const LEAN_TEXT_COLORS: Record<number, string> = {
  [-2]: 'text-blue-600',
  [-1]: 'text-blue-500',
  [0]: 'text-purple-500',
  [1]: 'text-red-500',
  [2]: 'text-red-600',
};
