import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import {
  Database,
  Filter,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { listSources } from '../services/api';
import type { SourceFilters } from '../types';
import { PageHeader, Card, LoadingSpinner, ErrorMessage, EmptyState } from '../components/Layout';
import { SourceCard, SourceCardGrid } from '../components/SourceCard';
import { clsx } from 'clsx';

const LEAN_OPTIONS = [
  { value: -2, label: 'Left' },
  { value: -1, label: 'Lean Left' },
  { value: 0, label: 'Center' },
  { value: 1, label: 'Lean Right' },
  { value: 2, label: 'Right' },
];

const CREDIBILITY_OPTIONS = [
  { value: undefined, label: 'Any' },
  { value: 60, label: '60+ (Medium)' },
  { value: 70, label: '70+' },
  { value: 80, label: '80+ (High)' },
  { value: 90, label: '90+' },
];

const SOURCE_TYPE_OPTIONS = [
  { value: undefined, label: 'All Types' },
  { value: 'news_media', label: 'News Media' },
  { value: 'fact_check', label: 'Fact Check' },
  { value: 'trade_publication', label: 'Trade Publication' },
  { value: 'think_tank', label: 'Think Tank' },
  { value: 'author', label: 'Author' },
];

const PAGE_SIZE = 24;

export function Sources() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse filters from URL
  const [filters, setFilters] = useState<SourceFilters>(() => ({
    lean: searchParams.get('lean') ? Number(searchParams.get('lean')) : undefined,
    min_credibility: searchParams.get('min_credibility') ? Number(searchParams.get('min_credibility')) : undefined,
    source_type: searchParams.get('source_type') || undefined,
    limit: PAGE_SIZE,
    offset: searchParams.get('offset') ? Number(searchParams.get('offset')) : 0,
  }));

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.lean !== undefined) params.set('lean', String(filters.lean));
    if (filters.min_credibility !== undefined) params.set('min_credibility', String(filters.min_credibility));
    if (filters.source_type) params.set('source_type', filters.source_type);
    if (filters.offset) params.set('offset', String(filters.offset));
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['sources', filters],
    queryFn: () => listSources(filters),
  });

  const updateFilter = (key: keyof SourceFilters, value: unknown) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
      offset: key === 'offset' ? (value as number) : 0, // Reset pagination when filters change
    }));
  };

  const clearFilters = () => {
    setFilters({
      lean: undefined,
      min_credibility: undefined,
      source_type: undefined,
      limit: PAGE_SIZE,
      offset: 0,
    });
  };

  const hasFilters = filters.lean !== undefined || filters.min_credibility !== undefined || filters.source_type !== undefined;

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;
  const currentPage = Math.floor((filters.offset || 0) / PAGE_SIZE) + 1;

  return (
    <div>
      <PageHeader
        title="Browse Sources"
        description={`Explore and filter ${data?.total || 0} sources in the database`}
      />

      {/* Filters */}
      <Card className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <span className="font-medium text-gray-700">Filters</span>
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="ml-auto text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              <X className="w-4 h-4" />
              Clear all
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-4">
          {/* Political Lean */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Political Lean</label>
            <div className="flex gap-1">
              <button
                onClick={() => updateFilter('lean', undefined)}
                className={clsx(
                  'px-3 py-1.5 text-sm rounded-lg transition-colors',
                  filters.lean === undefined
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                )}
              >
                All
              </button>
              {LEAN_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => updateFilter('lean', option.value)}
                  className={clsx(
                    'px-3 py-1.5 text-sm rounded-lg transition-colors',
                    filters.lean === option.value
                      ? getLeanButtonColor(option.value)
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Credibility */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Credibility</label>
            <select
              value={filters.min_credibility || ''}
              onChange={(e) => updateFilter('min_credibility', e.target.value ? Number(e.target.value) : undefined)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {CREDIBILITY_OPTIONS.map((option) => (
                <option key={option.label} value={option.value || ''}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Source Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
            <select
              value={filters.source_type || ''}
              onChange={(e) => updateFilter('source_type', e.target.value || undefined)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {SOURCE_TYPE_OPTIONS.map((option) => (
                <option key={option.label} value={option.value || ''}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Results */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {error && (
        <ErrorMessage message="Failed to load sources. Make sure the API is running." />
      )}

      {data && data.sources.length === 0 && (
        <EmptyState
          icon={Database}
          title="No sources found"
          description="Try adjusting your filters to see more results"
          action={
            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Clear filters
            </button>
          }
        />
      )}

      {data && data.sources.length > 0 && (
        <>
          {/* Results count */}
          <div className="mb-4 text-sm text-gray-500">
            Showing {(filters.offset || 0) + 1}-{Math.min((filters.offset || 0) + PAGE_SIZE, data.total)} of {data.total} sources
          </div>

          <SourceCardGrid>
            {data.sources.map((source) => (
              <SourceCard key={source.domain} source={source} />
            ))}
          </SourceCardGrid>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <button
                onClick={() => updateFilter('offset', Math.max(0, (filters.offset || 0) - PAGE_SIZE))}
                disabled={currentPage === 1}
                className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum: number;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => updateFilter('offset', (pageNum - 1) * PAGE_SIZE)}
                      className={clsx(
                        'w-10 h-10 rounded-lg text-sm font-medium transition-colors',
                        pageNum === currentPage
                          ? 'bg-blue-600 text-white'
                          : 'hover:bg-gray-100'
                      )}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={() => updateFilter('offset', (filters.offset || 0) + PAGE_SIZE)}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function getLeanButtonColor(lean: number): string {
  switch (lean) {
    case -2: return 'bg-blue-600 text-white';
    case -1: return 'bg-blue-400 text-white';
    case 0: return 'bg-purple-500 text-white';
    case 1: return 'bg-red-400 text-white';
    case 2: return 'bg-red-600 text-white';
    default: return 'bg-gray-800 text-white';
  }
}
