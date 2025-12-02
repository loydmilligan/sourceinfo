import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Search,
  ExternalLink,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  Info,
  Loader2,
  FileText,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  Scale,
  Flame,
  Quote,
  Brain,
} from 'lucide-react';
import { analyzeUrl, analyzeContent } from '../services/api';
import type { AnalyzeRequest, AnalyzeResponse, ContentAnalysisResponse } from '../types';
import { PageHeader, Card, ErrorMessage } from '../components/Layout';
import { BiasIndicator, BiasSpectrum } from '../components/BiasIndicator';
import { CredibilityDisplay } from '../components/CredibilityMeter';
import { SourceCard } from '../components/SourceCard';
import { clsx } from 'clsx';

export function Analyze() {
  const [url, setUrl] = useState('');
  const [includeCounternarratives, setIncludeCounternarratives] = useState(true);
  const [minCredibility, setMinCredibility] = useState(60);
  const [preferredLeans, setPreferredLeans] = useState<number[]>([]);

  const sourceMutation = useMutation({
    mutationFn: (request: AnalyzeRequest) => analyzeUrl(request),
  });

  const contentMutation = useMutation({
    mutationFn: (articleUrl: string) => analyzeContent({ url: articleUrl }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    // Reset content analysis when starting new source analysis
    contentMutation.reset();

    sourceMutation.mutate({
      url: url.trim(),
      include_counternarratives: includeCounternarratives,
      min_counternarrative_credibility: minCredibility,
      counternarrative_limit: 10,
      preferred_leans: preferredLeans.length > 0 ? preferredLeans : undefined,
    });
  };

  const handleContentAnalysis = () => {
    if (!url.trim()) return;
    contentMutation.mutate(url.trim());
  };

  const toggleLean = (lean: number) => {
    setPreferredLeans((prev) =>
      prev.includes(lean) ? prev.filter((l) => l !== lean) : [...prev, lean]
    );
  };

  return (
    <div>
      <PageHeader
        title="Analyze URL"
        description="Enter an article URL to get source information, credibility ratings, and content analysis"
      />

      {/* Input form */}
      <Card className="mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Article URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.nytimes.com/2024/article..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              />
              <button
                type="submit"
                disabled={sourceMutation.isPending || !url.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {sourceMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                Analyze
              </button>
            </div>
          </div>

          {/* Options */}
          <div className="border-t border-gray-100 pt-4 mt-4">
            <div className="flex flex-wrap items-center gap-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeCounternarratives}
                  onChange={(e) => setIncludeCounternarratives(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Include counternarratives</span>
              </label>

              {includeCounternarratives && (
                <>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">Min credibility:</label>
                    <select
                      value={minCredibility}
                      onChange={(e) => setMinCredibility(Number(e.target.value))}
                      className="px-2 py-1 border border-gray-300 rounded text-sm"
                    >
                      <option value={0}>Any</option>
                      <option value={60}>60+</option>
                      <option value={70}>70+</option>
                      <option value={80}>80+</option>
                      <option value={90}>90+</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-700">Prefer:</label>
                    <div className="flex gap-1">
                      {[
                        { value: 1, label: 'Lean Right', color: 'bg-red-400' },
                        { value: 2, label: 'Right', color: 'bg-red-600' },
                      ].map((option) => (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => toggleLean(option.value)}
                          className={clsx(
                            'px-2 py-1 text-xs rounded transition-colors',
                            preferredLeans.includes(option.value)
                              ? `${option.color} text-white`
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          )}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </form>
      </Card>

      {/* Results */}
      {sourceMutation.error && (
        <ErrorMessage message="Failed to analyze URL. Please check the URL and try again." />
      )}

      {sourceMutation.data && (
        <AnalyzeResults
          result={sourceMutation.data}
          contentAnalysis={contentMutation.data}
          contentLoading={contentMutation.isPending}
          contentError={contentMutation.error}
          onAnalyzeContent={handleContentAnalysis}
        />
      )}

      {/* Empty state */}
      {!sourceMutation.data && !sourceMutation.isPending && (
        <Card>
          <div className="text-center py-8">
            <Search className="w-12 h-12 text-gray-300 mx-auto" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">Enter a URL to analyze</h3>
            <p className="mt-2 text-gray-500">
              Paste any news article URL to see source credibility, political bias, and find counternarratives
            </p>
            <div className="mt-4 text-sm text-gray-400">
              Example: https://www.nytimes.com/2024/article-slug
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

interface AnalyzeResultsProps {
  result: AnalyzeResponse;
  contentAnalysis?: ContentAnalysisResponse;
  contentLoading: boolean;
  contentError: Error | null;
  onAnalyzeContent: () => void;
}

function AnalyzeResults({
  result,
  contentAnalysis,
  contentLoading,
  contentError,
  onAnalyzeContent,
}: AnalyzeResultsProps) {
  if (result.error && !result.source_found) {
    return (
      <Card>
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-yellow-500 flex-shrink-0" />
          <div>
            <h3 className="font-medium text-gray-900">Source Not Found</h3>
            <p className="mt-1 text-gray-600">
              The domain <code className="px-1 py-0.5 bg-gray-100 rounded">{result.domain}</code> is not in our database.
            </p>
            <p className="mt-2 text-sm text-gray-500">
              This could mean it's a newer source, a niche publication, or not yet rated by NewsGuard/AllSides.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const source = result.source!;

  return (
    <div className="space-y-6">
      {/* Source info */}
      <Card>
        <div className="flex items-start gap-2 mb-4">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
          <span className="text-sm text-green-600">Source found in database</span>
        </div>

        <div className="flex flex-col lg:flex-row lg:items-start gap-6">
          {/* Left: Source details */}
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">{source.name}</h2>
            <div className="flex items-center gap-2 mt-2">
              <a
                href={`https://${source.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                {source.domain}
                <ExternalLink className="w-4 h-4" />
              </a>
              {source.source_type && (
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-sm">
                  {source.source_type.replace(/_/g, ' ')}
                </span>
              )}
            </div>

            {source.description && (
              <p className="mt-4 text-gray-600">{source.description}</p>
            )}

            <div className="mt-4">
              <Link
                to={`/sources/${encodeURIComponent(source.domain)}`}
                className="text-blue-600 hover:text-blue-700 flex items-center gap-1 text-sm"
              >
                View full source details
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Right: Ratings */}
          <div className="lg:w-64 space-y-6">
            {/* Credibility */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Credibility</h3>
              <CredibilityDisplay score={source.newsguard_score} rating={source.newsguard_rating} />
            </div>

            {/* Political lean */}
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">Political Lean</h3>
              <BiasSpectrum lean={source.political_lean} />
              <div className="mt-2">
                <BiasIndicator lean={source.political_lean} size="lg" />
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Content Analysis Section */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg font-semibold text-gray-900">Article Content Analysis</h3>
          </div>
          {!contentAnalysis && !contentLoading && (
            <button
              onClick={onAnalyzeContent}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 text-sm"
            >
              <Brain className="w-4 h-4" />
              Analyze Content
            </button>
          )}
        </div>

        {!contentAnalysis && !contentLoading && !contentError && (
          <p className="text-gray-600">
            Click "Analyze Content" to fetch the article and analyze it for inflammatory language,
            unsupported claims, emotional manipulation, and bias indicators.
          </p>
        )}

        {contentLoading && (
          <div className="flex items-center gap-3 py-8 justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
            <span className="text-gray-600">Fetching and analyzing article content...</span>
          </div>
        )}

        {contentError && (
          <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <div>
              <p className="font-medium text-red-800">Analysis failed</p>
              <p className="text-sm text-red-600">Could not fetch or analyze the article content.</p>
            </div>
          </div>
        )}

        {contentAnalysis && <ContentAnalysisResults analysis={contentAnalysis} />}
      </Card>

      {/* Counternarratives */}
      {result.counternarratives && result.counternarratives.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <Info className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">Counternarrative Sources</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Credible sources from the opposite political perspective that may cover this topic differently:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.counternarratives.map((counter) => (
              <SourceCard
                key={counter.domain}
                source={counter}
                showDescription={false}
                showWeightedScore={true}
                compact={false}
              />
            ))}
          </div>
        </Card>
      )}

      {result.counternarratives && result.counternarratives.length === 0 && (
        <Card>
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-blue-500 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-gray-900">No Counternarratives Available</h3>
              <p className="mt-1 text-gray-600">
                {source.political_lean === 0
                  ? 'This source is rated as Center, so counternarratives from both sides could be relevant.'
                  : 'No credible opposite-perspective sources matched your criteria. Try lowering the minimum credibility.'}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

function ContentAnalysisResults({ analysis }: { analysis: ContentAnalysisResponse }) {
  if (!analysis.success) {
    return (
      <div className="flex items-start gap-3 p-4 bg-yellow-50 rounded-lg">
        <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
        <div>
          <p className="font-medium text-yellow-800">Could not analyze content</p>
          <p className="text-sm text-yellow-700">{analysis.error}</p>
        </div>
      </div>
    );
  }

  const scores = analysis.scores;

  return (
    <div className="space-y-6">
      {/* Summary */}
      {analysis.summary && (
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2">Summary</h4>
          <p className="text-gray-700">{analysis.summary}</p>
        </div>
      )}

      {/* Overall Score */}
      {scores && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <ScoreCard
            label="Overall"
            score={scores.overall_quality}
            maxScore={100}
            grade={scores.overall_grade}
            colorClass={getOverallColorClass(scores.overall_quality)}
          />
          <ScoreCard
            label="Inflammatory"
            score={scores.inflammatory_language}
            maxScore={10}
            inverted
            icon={<Flame className="w-4 h-4" />}
          />
          <ScoreCard
            label="Unsupported"
            score={scores.unsupported_claims}
            maxScore={10}
            inverted
            icon={<Quote className="w-4 h-4" />}
          />
          <ScoreCard
            label="Manipulation"
            score={scores.emotional_manipulation}
            maxScore={10}
            inverted
            icon={<Brain className="w-4 h-4" />}
          />
          <ScoreCard
            label="Factual"
            score={scores.factual_reporting}
            maxScore={10}
            icon={<CheckCircle className="w-4 h-4" />}
          />
          <ScoreCard
            label="Bias"
            score={analysis.detected_bias || 'Unknown'}
            isText
            icon={<Scale className="w-4 h-4" />}
          />
        </div>
      )}

      {/* Detailed Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inflammatory Language */}
        {(analysis.inflammatory_examples.length > 0 || analysis.inflammatory_explanation) && (
          <FindingCard
            title="Inflammatory Language"
            icon={<Flame className="w-5 h-5 text-orange-500" />}
            explanation={analysis.inflammatory_explanation}
            items={analysis.inflammatory_examples}
            itemType="quote"
          />
        )}

        {/* Unsupported Claims */}
        {(analysis.unsupported_claims.length > 0 || analysis.claims_explanation) && (
          <FindingCard
            title="Unsupported Claims"
            icon={<Quote className="w-5 h-5 text-yellow-500" />}
            explanation={analysis.claims_explanation}
            claims={analysis.unsupported_claims}
          />
        )}

        {/* Manipulation Techniques */}
        {(analysis.manipulation_techniques.length > 0 || analysis.manipulation_explanation) && (
          <FindingCard
            title="Emotional Manipulation"
            icon={<Brain className="w-5 h-5 text-purple-500" />}
            explanation={analysis.manipulation_explanation}
            items={analysis.manipulation_techniques}
            itemType="technique"
          />
        )}

        {/* Bias Indicators */}
        {(analysis.bias_indicators.length > 0 || analysis.bias_explanation) && (
          <FindingCard
            title="Bias Indicators"
            icon={<Scale className="w-5 h-5 text-blue-500" />}
            explanation={analysis.bias_explanation}
            items={analysis.bias_indicators}
            itemType="indicator"
          />
        )}
      </div>

      {/* Factual Reporting */}
      {(analysis.factual_strengths.length > 0 || analysis.factual_weaknesses.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysis.factual_strengths.length > 0 && (
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsUp className="w-4 h-4 text-green-600" />
                <h4 className="font-medium text-green-800">Strengths</h4>
              </div>
              <ul className="space-y-1">
                {analysis.factual_strengths.map((item, i) => (
                  <li key={i} className="text-sm text-green-700">• {item}</li>
                ))}
              </ul>
            </div>
          )}
          {analysis.factual_weaknesses.length > 0 && (
            <div className="p-4 bg-red-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsDown className="w-4 h-4 text-red-600" />
                <h4 className="font-medium text-red-800">Weaknesses</h4>
              </div>
              <ul className="space-y-1">
                {analysis.factual_weaknesses.map((item, i) => (
                  <li key={i} className="text-sm text-red-700">• {item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Recommendation */}
      {analysis.recommendation && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-1">Recommendation</h4>
          <p className="text-gray-700">{analysis.recommendation}</p>
        </div>
      )}

      {/* Metadata */}
      <div className="text-xs text-gray-400 flex flex-wrap gap-4">
        {analysis.word_count && <span>Words: {analysis.word_count.toLocaleString()}</span>}
        {analysis.fetch_method && <span>Fetched via: {analysis.fetch_method}</span>}
        {analysis.model_used && <span>Model: {analysis.model_used}</span>}
      </div>
    </div>
  );
}

interface ScoreCardProps {
  label: string;
  score: number | string;
  maxScore?: number;
  grade?: string;
  inverted?: boolean;
  isText?: boolean;
  icon?: React.ReactNode;
  colorClass?: string;
}

function ScoreCard({ label, score, maxScore, grade, inverted, isText, icon, colorClass }: ScoreCardProps) {
  let bgClass = 'bg-gray-100';
  let textClass = 'text-gray-700';

  if (!isText && typeof score === 'number' && maxScore) {
    const pct = score / maxScore;
    if (inverted) {
      // Lower is better
      if (pct <= 0.3) { bgClass = 'bg-green-100'; textClass = 'text-green-700'; }
      else if (pct <= 0.6) { bgClass = 'bg-yellow-100'; textClass = 'text-yellow-700'; }
      else { bgClass = 'bg-red-100'; textClass = 'text-red-700'; }
    } else {
      // Higher is better
      if (pct >= 0.7) { bgClass = 'bg-green-100'; textClass = 'text-green-700'; }
      else if (pct >= 0.4) { bgClass = 'bg-yellow-100'; textClass = 'text-yellow-700'; }
      else { bgClass = 'bg-red-100'; textClass = 'text-red-700'; }
    }
  }

  if (colorClass) {
    bgClass = colorClass;
  }

  return (
    <div className={clsx('p-3 rounded-lg text-center', bgClass)}>
      <div className="flex items-center justify-center gap-1 mb-1">
        {icon}
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <div className={clsx('text-xl font-bold', textClass)}>
        {isText ? score : `${score}${maxScore ? `/${maxScore}` : ''}`}
      </div>
      {grade && <div className="text-sm font-medium text-gray-600">Grade: {grade}</div>}
    </div>
  );
}

interface FindingCardProps {
  title: string;
  icon: React.ReactNode;
  explanation?: string | null;
  items?: string[];
  claims?: Array<{ claim: string; issue: string }>;
  itemType?: 'quote' | 'technique' | 'indicator';
}

function FindingCard({ title, icon, explanation, items, claims, itemType }: FindingCardProps) {
  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h4 className="font-medium text-gray-900">{title}</h4>
      </div>
      {explanation && (
        <p className="text-sm text-gray-600 mb-3">{explanation}</p>
      )}
      {items && items.length > 0 && (
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
              <span className="text-gray-400">
                {itemType === 'quote' ? '"' : '•'}
              </span>
              <span className={itemType === 'quote' ? 'italic' : ''}>
                {item}
                {itemType === 'quote' ? '"' : ''}
              </span>
            </li>
          ))}
        </ul>
      )}
      {claims && claims.length > 0 && (
        <ul className="space-y-3">
          {claims.map((claim, i) => (
            <li key={i} className="text-sm">
              <p className="text-gray-700 font-medium">"{claim.claim}"</p>
              <p className="text-gray-500 text-xs mt-1">Issue: {claim.issue}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function getOverallColorClass(score: number): string {
  if (score >= 80) return 'bg-green-100';
  if (score >= 60) return 'bg-yellow-100';
  if (score >= 40) return 'bg-orange-100';
  return 'bg-red-100';
}
