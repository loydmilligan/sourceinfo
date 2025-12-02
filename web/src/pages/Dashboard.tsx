import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Database,
  Shield,
  TrendingUp,
  Users,
  ArrowRight,
  Search,
  DollarSign,
} from 'lucide-react';
import { getStats, getUsageStats } from '../services/api';
import { PageHeader, Card, LoadingSpinner, ErrorMessage } from '../components/Layout';
import { clsx } from 'clsx';

export function Dashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
  });

  const { data: usageStats } = useQuery({
    queryKey: ['usage-stats', 30],
    queryFn: () => getUsageStats(30),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message="Failed to load statistics. Make sure the API is running." />;
  }

  if (!stats) return null;

  const leanOrder = ['Left', 'Lean Left', 'Center', 'Lean Right', 'Right'];
  const leanColorMap: Record<string, string> = {
    'Left': 'bg-blue-600',
    'Lean Left': 'bg-blue-400',
    'Center': 'bg-purple-500',
    'Lean Right': 'bg-red-400',
    'Right': 'bg-red-600',
  };

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of the SourceInfo database"
      />

      {/* Quick actions */}
      <div className="mb-8 flex flex-wrap gap-4">
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Search className="w-4 h-4" />
          Analyze URL
        </Link>
        <Link
          to="/sources"
          className="inline-flex items-center gap-2 px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Database className="w-4 h-4" />
          Browse Sources
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.total_sources}</div>
              <div className="text-sm text-gray-500">Total Sources</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.with_newsguard}</div>
              <div className="text-sm text-gray-500">With Credibility Ratings</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.with_political_lean}</div>
              <div className="text-sm text-gray-500">With Political Lean</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Users className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.credibility_tiers.high}</div>
              <div className="text-sm text-gray-500">High Credibility</div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Political lean distribution */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Political Lean Distribution</h2>
          <div className="space-y-3">
            {leanOrder.map((lean) => {
              const count = stats.lean_distribution[lean] || 0;
              const percentage = Math.round((count / stats.with_political_lean) * 100);
              return (
                <div key={lean}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{lean}</span>
                    <span className="text-gray-500">{count} ({percentage}%)</span>
                  </div>
                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={clsx('h-full rounded-full transition-all', leanColorMap[lean])}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link
              to="/sources?lean=0"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              View Center sources
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </Card>

        {/* Credibility tiers */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Credibility Tiers</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-xl font-bold text-green-600">{stats.credibility_tiers.high}</span>
              </div>
              <div>
                <div className="font-medium text-gray-900">High (80-100)</div>
                <div className="text-sm text-gray-500">Strong credibility, recommended</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-yellow-100 flex items-center justify-center">
                <span className="text-xl font-bold text-yellow-600">{stats.credibility_tiers.medium}</span>
              </div>
              <div>
                <div className="font-medium text-gray-900">Medium (60-79)</div>
                <div className="text-sm text-gray-500">Acceptable, use with context</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
                <span className="text-xl font-bold text-red-600">{stats.credibility_tiers.low}</span>
              </div>
              <div>
                <div className="font-medium text-gray-900">Low (0-59)</div>
                <div className="text-sm text-gray-500">Use with caution</div>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link
              to="/sources?min_credibility=80"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              View high-credibility sources
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </Card>

        {/* Source types */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Source Types</h2>
          <div className="space-y-2">
            {Object.entries(stats.type_distribution)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count]) => (
                <div key={type} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <span className="text-gray-700 capitalize">{type.replace(/_/g, ' ')}</span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm font-medium">
                    {count}
                  </span>
                </div>
              ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link
              to="/sources?source_type=fact_check"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              View fact-checkers
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </Card>

        {/* API Usage & Costs */}
        {usageStats && (
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="w-5 h-5 text-green-500" />
              <h2 className="text-lg font-semibold text-gray-900">API Usage & Costs (30 days)</h2>
            </div>
            <div className="space-y-4">
              {/* Total cost */}
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total Cost</span>
                <span className="text-2xl font-bold text-gray-900">
                  ${usageStats.totals.total_cost.toFixed(4)}
                </span>
              </div>

              {/* API calls */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Total Calls</span>
                <span className="font-medium text-gray-900">{usageStats.totals.total_calls}</span>
              </div>

              {/* Success rate */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Success Rate</span>
                <span className="font-medium text-gray-900">
                  {usageStats.totals.total_calls > 0
                    ? `${Math.round((usageStats.totals.successful_calls / usageStats.totals.total_calls) * 100)}%`
                    : 'N/A'}
                </span>
              </div>

              {/* Tokens */}
              {usageStats.totals.total_input_tokens > 0 && (
                <div className="pt-3 border-t border-gray-100">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">Input Tokens</span>
                    <span className="font-medium text-gray-700">
                      {usageStats.totals.total_input_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Output Tokens</span>
                    <span className="font-medium text-gray-700">
                      {usageStats.totals.total_output_tokens.toLocaleString()}
                    </span>
                  </div>
                </div>
              )}

              {/* Breakdown by model */}
              {usageStats.by_model.length > 0 && (
                <div className="pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-500 mb-2">By Model:</p>
                  {usageStats.by_model.slice(0, 3).map((model) => (
                    <div key={model.model_used} className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-600 truncate">{model.model_used.split('/')[1]}</span>
                      <span className="font-medium text-gray-700">${model.cost.toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Quick tips */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Tips</h2>
          <div className="space-y-4 text-sm text-gray-600">
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-medium">1</span>
              </div>
              <p>
                <strong>Analyze URLs</strong> - Paste any article URL to instantly see source credibility and bias.
              </p>
            </div>
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-medium">2</span>
              </div>
              <p>
                <strong>Find counternarratives</strong> - Get credible sources from opposing viewpoints for balanced coverage.
              </p>
            </div>
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-medium">3</span>
              </div>
              <p>
                <strong>Filter by credibility</strong> - Focus on high-credibility sources for evidence in claim analysis.
              </p>
            </div>
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-medium">4</span>
              </div>
              <p>
                <strong>Use the API</strong> - Integrate with your apps via REST API at <code className="px-1 py-0.5 bg-gray-100 rounded">/api</code>
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
