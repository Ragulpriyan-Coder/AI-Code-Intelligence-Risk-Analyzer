/**
 * Score card component for displaying metrics.
 */
import React from 'react';
import { Shield, Code, Boxes, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  score: number;
  type: 'security' | 'maintainability' | 'architecture' | 'debt';
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const ScoreCard: React.FC<ScoreCardProps> = ({ title, score, type, subtitle, trend }) => {
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-cyan-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  const getGradient = (score: number): string => {
    if (score >= 80) return 'from-green-500/20 to-green-500/5';
    if (score >= 60) return 'from-cyan-500/20 to-cyan-500/5';
    if (score >= 40) return 'from-amber-500/20 to-amber-500/5';
    return 'from-red-500/20 to-red-500/5';
  };

  const getBorderColor = (score: number): string => {
    if (score >= 80) return 'border-green-500/30';
    if (score >= 60) return 'border-cyan-500/30';
    if (score >= 40) return 'border-amber-500/30';
    return 'border-red-500/30';
  };

  const getIcon = () => {
    const iconClass = 'w-6 h-6';
    switch (type) {
      case 'security':
        return <Shield className={iconClass} />;
      case 'maintainability':
        return <Code className={iconClass} />;
      case 'architecture':
        return <Boxes className={iconClass} />;
      case 'debt':
        return <AlertTriangle className={iconClass} />;
      default:
        return <Shield className={iconClass} />;
    }
  };

  const getGrade = (score: number): string => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  // For debt, invert the display (lower is better)
  const displayScore = type === 'debt' ? score : score;
  const invertedForDebt = type === 'debt';

  return (
    <div
      className={`glass-card p-6 bg-gradient-to-br ${getGradient(invertedForDebt ? 100 - score : score)}
                  border ${getBorderColor(invertedForDebt ? 100 - score : score)}
                  transition-all duration-300 hover:scale-105 hover:shadow-glow`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg bg-dark-800/50 ${getScoreColor(invertedForDebt ? 100 - score : score)}`}>
          {getIcon()}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${
            trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'
          }`}>
            {trend === 'up' ? <TrendingUp className="w-4 h-4" /> :
             trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
          </div>
        )}
      </div>

      {/* Score */}
      <div className="mb-2">
        <span className={`text-5xl font-bold ${getScoreColor(invertedForDebt ? 100 - score : score)}`}>
          {Math.round(displayScore)}
        </span>
        <span className="text-2xl text-gray-500 ml-1">/100</span>
      </div>

      {/* Title and subtitle */}
      <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
      {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}

      {/* Grade badge */}
      <div className="mt-4 flex items-center gap-2">
        <span className={`px-2 py-1 rounded text-xs font-bold bg-dark-800 ${getScoreColor(invertedForDebt ? 100 - score : score)}`}>
          Grade: {getGrade(invertedForDebt ? 100 - score : score)}
        </span>
      </div>
    </div>
  );
};

// Urgency badge component
interface UrgencyBadgeProps {
  urgency: 'Low' | 'Medium' | 'High' | 'Critical' | string;
  size?: 'sm' | 'md' | 'lg';
}

export const UrgencyBadge: React.FC<UrgencyBadgeProps> = ({ urgency, size = 'md' }) => {
  const getUrgencyStyles = (urgency: string): string => {
    switch (urgency) {
      case 'Low':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'High':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'Critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-full border font-medium
                     ${getUrgencyStyles(urgency)} ${sizeClasses[size]}`}>
      <AlertTriangle className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
      {urgency}
    </span>
  );
};

export default ScoreCard;
