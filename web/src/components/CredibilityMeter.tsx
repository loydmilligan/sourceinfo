import { clsx } from 'clsx';

interface CredibilityMeterProps {
  score: number | null;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  showBar?: boolean;
}

function getCredibilityTier(score: number | null): { tier: string; color: string; bgColor: string } {
  if (score === null) {
    return { tier: 'Unknown', color: 'text-gray-500', bgColor: 'bg-gray-200' };
  }
  if (score >= 80) {
    return { tier: 'High', color: 'text-green-600', bgColor: 'bg-green-500' };
  }
  if (score >= 60) {
    return { tier: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-500' };
  }
  return { tier: 'Low', color: 'text-red-600', bgColor: 'bg-red-500' };
}

function getScoreColor(score: number | null): string {
  if (score === null) return 'text-gray-400';
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-red-600';
}

export function CredibilityMeter({ score, size = 'md', showLabel = true, showBar = true }: CredibilityMeterProps) {
  const { tier, color, bgColor } = getCredibilityTier(score);
  const scoreColor = getScoreColor(score);

  return (
    <div className={clsx(
      'flex flex-col gap-1',
      size === 'sm' && 'text-xs',
      size === 'md' && 'text-sm',
      size === 'lg' && 'text-base'
    )}>
      <div className="flex items-center justify-between">
        <span className={clsx('font-bold', scoreColor)}>
          {score !== null ? `${score}/100` : 'N/A'}
        </span>
        {showLabel && (
          <span className={clsx('font-medium', color)}>
            {tier}
          </span>
        )}
      </div>
      {showBar && (
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={clsx('h-full rounded-full transition-all', bgColor)}
            style={{ width: score !== null ? `${score}%` : '0%' }}
          />
        </div>
      )}
    </div>
  );
}

// Compact score badge
export function CredibilityBadge({ score, size = 'md' }: { score: number | null; size?: 'sm' | 'md' | 'lg' }) {
  const { bgColor } = getCredibilityTier(score);

  if (score === null) {
    return (
      <span className={clsx(
        'inline-flex items-center rounded-full bg-gray-100 text-gray-500 font-medium',
        size === 'sm' && 'px-2 py-0.5 text-xs',
        size === 'md' && 'px-2.5 py-1 text-sm',
        size === 'lg' && 'px-3 py-1.5 text-base'
      )}>
        N/A
      </span>
    );
  }

  return (
    <span className={clsx(
      'inline-flex items-center rounded-full text-white font-medium',
      bgColor,
      size === 'sm' && 'px-2 py-0.5 text-xs',
      size === 'md' && 'px-2.5 py-1 text-sm',
      size === 'lg' && 'px-3 py-1.5 text-base'
    )}>
      {score}
    </span>
  );
}

// Full credibility display with rating text
export function CredibilityDisplay({ score, rating }: { score: number | null; rating: string | null }) {
  const { color } = getCredibilityTier(score);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline gap-2">
        <span className={clsx('text-3xl font-bold', getScoreColor(score))}>
          {score !== null ? score : '—'}
        </span>
        <span className="text-gray-400">/100</span>
      </div>
      {rating && (
        <span className={clsx('font-medium', color)}>
          {rating}
        </span>
      )}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full transition-all',
            score !== null && score >= 80 && 'bg-green-500',
            score !== null && score >= 60 && score < 80 && 'bg-yellow-500',
            score !== null && score < 60 && 'bg-red-500'
          )}
          style={{ width: score !== null ? `${score}%` : '0%' }}
        />
      </div>
    </div>
  );
}
