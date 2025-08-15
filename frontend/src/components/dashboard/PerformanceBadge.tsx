/**
 * Performance Badge Component
 * 
 * Displays student performance bands with appropriate color coding and score display.
 * Provides consistent visual indication of student academic performance.
 */

import { PerformanceBand, getPerformanceBadgeVariant } from '@/lib/schemas';
import { Badge } from '@/components/ui/badge';
import { Star, Trophy, Target, AlertTriangle } from 'lucide-react';

interface PerformanceBadgeProps {
  band: PerformanceBand;
  score: number;
  showIcon?: boolean;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'badge' | 'card' | 'minimal';
}

/**
 * Get icon for performance band
 */
function getPerformanceIcon(band: PerformanceBand) {
  switch (band) {
    case 'Outstanding':
      return <Star className="h-3 w-3" />;
    case 'Good':
      return <Trophy className="h-3 w-3" />;
    case 'Satisfactory':
      return <Target className="h-3 w-3" />;
    case 'Needs Improvement':
      return <AlertTriangle className="h-3 w-3" />;
    default:
      return null;
  }
}

/**
 * Get color classes for custom styling
 */
function getPerformanceColors(band: PerformanceBand) {
  switch (band) {
    case 'Outstanding':
      return {
        text: 'text-green-700',
        bg: 'bg-green-50',
        border: 'border-green-200',
        icon: 'text-green-500',
        score: 'text-green-600'
      };
    case 'Good':
      return {
        text: 'text-blue-700',
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: 'text-blue-500',
        score: 'text-blue-600'
      };
    case 'Satisfactory':
      return {
        text: 'text-yellow-700',
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        icon: 'text-yellow-500',
        score: 'text-yellow-600'
      };
    case 'Needs Improvement':
      return {
        text: 'text-red-700',
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: 'text-red-500',
        score: 'text-red-600'
      };
    default:
      return {
        text: 'text-gray-700',
        bg: 'bg-gray-50',
        border: 'border-gray-200',
        icon: 'text-gray-500',
        score: 'text-gray-600'
      };
  }
}

/**
 * Get performance band description
 */
function getPerformanceDescription(band: PerformanceBand): string {
  switch (band) {
    case 'Outstanding':
      return 'Excellent academic performance (≥85%)';
    case 'Good':
      return 'Good academic performance (70-84%)';
    case 'Satisfactory':
      return 'Satisfactory academic performance (55-69%)';
    case 'Needs Improvement':
      return 'Requires additional support (<55%)';
    default:
      return 'Performance level not determined';
  }
}

/**
 * Badge variant - Simple badge display
 */
function BadgeVariant({ band, score, showIcon, showScore }: PerformanceBadgeProps) {
  const variant = getPerformanceBadgeVariant(band);
  const icon = showIcon ? getPerformanceIcon(band) : null;

  return (
    <div className="flex items-center gap-2">
      <Badge variant={variant} className="flex items-center gap-1">
        {icon}
        <span>{band}</span>
      </Badge>
      {showScore && (
        <span className="text-sm font-medium text-gray-600">
          {score.toFixed(1)}%
        </span>
      )}
    </div>
  );
}

/**
 * Card variant - More detailed card display
 */
function CardVariant({ band, score, showIcon = true, showScore = true }: PerformanceBadgeProps) {
  const colors = getPerformanceColors(band);
  const icon = showIcon ? getPerformanceIcon(band) : null;
  const description = getPerformanceDescription(band);

  return (
    <div className={`${colors.bg} ${colors.border} border rounded-lg p-3`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon && <div className={colors.icon}>{icon}</div>}
          <span className={`font-medium ${colors.text}`}>{band}</span>
        </div>
        {showScore && (
          <span className={`font-bold ${colors.score}`}>
            {score.toFixed(1)}%
          </span>
        )}
      </div>
      <p className={`text-sm ${colors.text} opacity-80`}>{description}</p>
    </div>
  );
}

/**
 * Minimal variant - Just text and score
 */
function MinimalVariant({ band, score, showScore = true }: PerformanceBadgeProps) {
  const colors = getPerformanceColors(band);

  return (
    <div className="flex items-center gap-2">
      <span className={`text-sm font-medium ${colors.text}`}>{band}</span>
      {showScore && (
        <span className={`text-sm ${colors.score}`}>
          {score.toFixed(1)}%
        </span>
      )}
    </div>
  );
}

/**
 * Main Performance Badge Component
 */
export function PerformanceBadge({
  band,
  score,
  showIcon = false,
  showScore = true,
  size = 'md',
  variant = 'badge'
}: PerformanceBadgeProps) {
  // Render based on variant
  switch (variant) {
    case 'card':
      return <CardVariant band={band} score={score} showIcon={showIcon} showScore={showScore} />;
    case 'minimal':
      return <MinimalVariant band={band} score={score} showScore={showScore} />;
    case 'badge':
    default:
      return <BadgeVariant band={band} score={score} showIcon={showIcon} showScore={showScore} />;
  }
}

/**
 * Performance Badge with Tooltip
 * Shows additional information on hover
 */
interface PerformanceBadgeWithTooltipProps extends PerformanceBadgeProps {
  studentName?: string;
  className?: string;
}

export function PerformanceBadgeWithTooltip({
  band,
  score,
  studentName,
  className = '',
  ...props
}: PerformanceBadgeWithTooltipProps) {
  const description = getPerformanceDescription(band);
  
  return (
    <div 
      className={`group relative ${className}`}
      title={`${studentName ? studentName + ': ' : ''}${description}`}
    >
      <PerformanceBadge band={band} score={score} {...props} />
      
      {/* Tooltip */}
      <div className="invisible group-hover:visible absolute z-10 w-64 p-2 mt-1 text-sm bg-gray-900 text-white rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
        {studentName && (
          <div className="font-medium mb-1">{studentName}</div>
        )}
        <div className="mb-1">{band}: {score.toFixed(1)}%</div>
        <div className="text-gray-300">{description}</div>
      </div>
    </div>
  );
}

export default PerformanceBadge;