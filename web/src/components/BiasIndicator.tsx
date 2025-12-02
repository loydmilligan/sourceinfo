import { clsx } from 'clsx';
import { LEAN_LABELS, LEAN_COLORS, LEAN_TEXT_COLORS } from '../types';

interface BiasIndicatorProps {
  lean: number | null;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  showScale?: boolean;
}

export function BiasIndicator({ lean, size = 'md', showLabel = true, showScale = false }: BiasIndicatorProps) {
  if (lean === null || lean === undefined) {
    return (
      <span className={clsx(
        'inline-flex items-center rounded-full bg-gray-100 text-gray-500',
        size === 'sm' && 'px-2 py-0.5 text-xs',
        size === 'md' && 'px-2.5 py-1 text-sm',
        size === 'lg' && 'px-3 py-1.5 text-base'
      )}>
        Unknown
      </span>
    );
  }

  const label = LEAN_LABELS[lean] || 'Unknown';
  const bgColor = LEAN_COLORS[lean] || 'bg-gray-400';

  if (showScale) {
    return (
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1">
          {[-2, -1, 0, 1, 2].map((l) => (
            <div
              key={l}
              className={clsx(
                'h-2 w-6 rounded-sm transition-all',
                l === lean ? LEAN_COLORS[l] : 'bg-gray-200',
                l === lean && 'ring-2 ring-offset-1 ring-gray-400'
              )}
              title={LEAN_LABELS[l]}
            />
          ))}
        </div>
        {showLabel && (
          <span className={clsx('text-sm font-medium', LEAN_TEXT_COLORS[lean])}>
            {label}
          </span>
        )}
      </div>
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
      {showLabel ? label : lean}
    </span>
  );
}

// Full bias spectrum component
export function BiasSpectrum({ lean }: { lean: number | null }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex justify-between text-xs text-gray-500">
        <span>Left</span>
        <span>Center</span>
        <span>Right</span>
      </div>
      <div className="flex h-3 rounded-full overflow-hidden">
        <div className="flex-1 bg-blue-600" />
        <div className="flex-1 bg-blue-400" />
        <div className="flex-1 bg-purple-500" />
        <div className="flex-1 bg-red-400" />
        <div className="flex-1 bg-red-600" />
      </div>
      {lean !== null && (
        <div className="relative h-0">
          <div
            className="absolute -top-5 transform -translate-x-1/2"
            style={{ left: `${((lean + 2) / 4) * 100}%` }}
          >
            <div className="w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-800" />
          </div>
        </div>
      )}
    </div>
  );
}
