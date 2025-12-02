import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  ExternalLink,
  Building2,
  Info,
  CheckCircle,
  XCircle,
  MinusCircle,
} from 'lucide-react';
import { getSource, getCounternarratives } from '../services/api';
import { PageHeader, Card, LoadingSpinner, ErrorMessage } from '../components/Layout';
import { BiasIndicator, BiasSpectrum } from '../components/BiasIndicator';
import { CredibilityDisplay } from '../components/CredibilityMeter';
import { SourceCard, SourceCardGrid } from '../components/SourceCard';
import { clsx } from 'clsx';

export function SourceDetail() {
  const { domain } = useParams<{ domain: string }>();

  const { data: source, isLoading: sourceLoading, error: sourceError } = useQuery({
    queryKey: ['source', domain],
    queryFn: () => getSource(domain!),
    enabled: !!domain,
  });

  const { data: counternarratives } = useQuery({
    queryKey: ['counternarratives', domain],
    queryFn: () => getCounternarratives(domain!, { min_credibility: 60, limit: 6 }),
    enabled: !!domain && !!source,
  });

  if (sourceLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (sourceError || !source) {
    return (
      <div>
        <Link to="/sources" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to sources
        </Link>
        <ErrorMessage message={`Source not found: ${domain}`} />
      </div>
    );
  }

  return (
    <div>
      <Link to="/sources" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="w-4 h-4" />
        Back to sources
      </Link>

      <PageHeader
        title={source.name}
        description={
          <div className="flex items-center gap-3 mt-2">
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
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-sm capitalize">
                {source.source_type.replace(/_/g, ' ')}
              </span>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          {source.description && (
            <Card>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">About</h2>
              <p className="text-gray-600">{source.description}</p>
            </Card>
          )}

          {/* NewsGuard Criteria */}
          {source.criteria && (
            <Card>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">NewsGuard Criteria</h2>
              <div className="space-y-3">
                {Object.entries(source.criteria).map(([key, value]: [string, any]) => (
                  <CriteriaItem key={key} name={key} data={value} />
                ))}
              </div>
            </Card>
          )}

          {/* Ownership */}
          {source.ownership_summary && (
            <Card>
              <div className="flex items-center gap-2 mb-3">
                <Building2 className="w-5 h-5 text-gray-400" />
                <h2 className="text-lg font-semibold text-gray-900">Ownership & Funding</h2>
              </div>
              <p className="text-gray-600 whitespace-pre-wrap">{source.ownership_summary}</p>
            </Card>
          )}

          {/* Counternarratives */}
          {counternarratives && counternarratives.counternarratives.length > 0 && (
            <Card>
              <div className="flex items-center gap-2 mb-4">
                <Info className="w-5 h-5 text-blue-500" />
                <h2 className="text-lg font-semibold text-gray-900">Counternarrative Sources</h2>
              </div>
              <p className="text-gray-600 mb-4">
                Credible sources from the opposite political perspective:
              </p>
              <SourceCardGrid>
                {counternarratives.counternarratives.map((counter) => (
                  <SourceCard
                    key={counter.domain}
                    source={counter}
                    showDescription={false}
                    showWeightedScore={true}
                  />
                ))}
              </SourceCardGrid>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Credibility Card */}
          <Card>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Credibility Rating</h3>
            <CredibilityDisplay
              score={source.newsguard_score}
              rating={source.newsguard_rating}
            />
          </Card>

          {/* Political Lean Card */}
          <Card>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Political Lean</h3>
            <div className="space-y-4">
              <BiasSpectrum lean={source.political_lean} />
              <div className="flex justify-center">
                <BiasIndicator lean={source.political_lean} size="lg" />
              </div>
            </div>
          </Card>

          {/* Quick Stats Card */}
          <Card>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Quick Stats</h3>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="text-gray-600">Domain</dt>
                <dd className="font-medium text-gray-900">{source.domain}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Type</dt>
                <dd className="font-medium text-gray-900 capitalize">
                  {source.source_type?.replace(/_/g, ' ') || 'N/A'}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Score</dt>
                <dd className="font-medium text-gray-900">
                  {source.newsguard_score !== null ? `${source.newsguard_score}/100` : 'N/A'}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Lean</dt>
                <dd className="font-medium text-gray-900">
                  {source.political_lean_label || 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>

          {/* Actions Card */}
          <Card>
            <h3 className="text-sm font-medium text-gray-500 mb-3">Actions</h3>
            <div className="space-y-2">
              <a
                href={`https://${source.domain}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Visit Website
              </a>
              <Link
                to={`/analyze?url=https://${source.domain}`}
                className="flex items-center justify-center gap-2 w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Analyze Article
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function CriteriaItem({ name, data }: { name: string; data: any }) {
  const formatName = (key: string) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const status = data?.status;
  const points = data?.points;

  const StatusIcon = status === 'pass' ? CheckCircle
    : status === 'fail' ? XCircle
    : MinusCircle;

  const statusColor = status === 'pass' ? 'text-green-500'
    : status === 'fail' ? 'text-red-500'
    : 'text-gray-400';

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
      <div className="flex items-center gap-3">
        <StatusIcon className={clsx('w-5 h-5', statusColor)} />
        <span className="text-gray-700">{formatName(name)}</span>
      </div>
      {points !== undefined && (
        <span className={clsx(
          'px-2 py-0.5 rounded text-sm font-medium',
          status === 'pass' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
        )}>
          {points} pts
        </span>
      )}
    </div>
  );
}
