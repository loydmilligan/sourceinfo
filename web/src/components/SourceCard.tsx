import { Link } from 'react-router-dom';
import { ExternalLink, ArrowRight } from 'lucide-react';
import { clsx } from 'clsx';
import type { Source, SourceWithScore } from '../types';
import { BiasIndicator } from './BiasIndicator';
import { CredibilityBadge } from './CredibilityMeter';

interface SourceCardProps {
  source: Source | SourceWithScore;
  showDescription?: boolean;
  showWeightedScore?: boolean;
  compact?: boolean;
}

export function SourceCard({ source, showDescription = true, showWeightedScore = false, compact = false }: SourceCardProps) {
  const weightedScore = 'weighted_score' in source ? source.weighted_score : null;

  if (compact) {
    return (
      <Link
        to={`/sources/${encodeURIComponent(source.domain)}`}
        className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all"
      >
        <div className="flex items-center gap-3">
          <div>
            <div className="font-medium text-gray-900">{source.name}</div>
            <div className="text-sm text-gray-500">{source.domain}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <CredibilityBadge score={source.newsguard_score} size="sm" />
          <BiasIndicator lean={source.political_lean} size="sm" />
        </div>
      </Link>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <Link
              to={`/sources/${encodeURIComponent(source.domain)}`}
              className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors"
            >
              {source.name}
            </Link>
            <div className="flex items-center gap-2 mt-1">
              <a
                href={`https://${source.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-500 hover:text-blue-500 flex items-center gap-1"
              >
                {source.domain}
                <ExternalLink className="w-3 h-3" />
              </a>
              {source.source_type && (
                <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                  {source.source_type.replace(/_/g, ' ')}
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <CredibilityBadge score={source.newsguard_score} />
            <BiasIndicator lean={source.political_lean} />
          </div>
        </div>

        {showDescription && source.description && (
          <p className="mt-3 text-sm text-gray-600 line-clamp-2">
            {source.description}
          </p>
        )}

        {showWeightedScore && weightedScore !== null && (
          <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
            <span className="text-sm text-gray-500">Weighted Score</span>
            <span className={clsx(
              'font-bold',
              weightedScore >= 80 && 'text-green-600',
              weightedScore >= 60 && weightedScore < 80 && 'text-yellow-600',
              weightedScore < 60 && 'text-red-600'
            )}>
              {weightedScore}/100
            </span>
          </div>
        )}
      </div>

      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
        <Link
          to={`/sources/${encodeURIComponent(source.domain)}`}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          View details
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

// Grid wrapper for source cards
export function SourceCardGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {children}
    </div>
  );
}

// List wrapper for compact source cards
export function SourceCardList({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2">
      {children}
    </div>
  );
}
