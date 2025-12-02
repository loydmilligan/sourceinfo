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
} from 'lucide-react';
import { analyzeUrl } from '../services/api';
import type { AnalyzeRequest, AnalyzeResponse } from '../types';
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

  const mutation = useMutation({
    mutationFn: (request: AnalyzeRequest) => analyzeUrl(request),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    mutation.mutate({
      url: url.trim(),
      include_counternarratives: includeCounternarratives,
      min_counternarrative_credibility: minCredibility,
      counternarrative_limit: 10,
      preferred_leans: preferredLeans.length > 0 ? preferredLeans : undefined,
    });
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
        description="Enter an article URL to get source information, credibility ratings, and counternarratives"
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
                disabled={mutation.isPending || !url.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {mutation.isPending ? (
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
      {mutation.error && (
        <ErrorMessage message="Failed to analyze URL. Please check the URL and try again." />
      )}

      {mutation.data && (
        <AnalyzeResults result={mutation.data} />
      )}

      {/* Empty state */}
      {!mutation.data && !mutation.isPending && (
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

function AnalyzeResults({ result }: { result: AnalyzeResponse }) {
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
