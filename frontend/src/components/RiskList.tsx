/**
 * Risk list component for displaying security issues and warnings.
 */
import React from 'react';
import { AlertTriangle, AlertCircle, Info, ChevronRight, FileCode, ExternalLink } from 'lucide-react';

interface RiskItem {
  id?: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | string;
  file?: string;
  line?: number;
  description?: string;
  recommendation?: string;
  cwe?: string;
}

interface RiskListProps {
  items: RiskItem[];
  title?: string;
  maxItems?: number;
}

const RiskList: React.FC<RiskListProps> = ({ items, title = 'Security Issues', maxItems = 10 }) => {
  const [expandedItem, setExpandedItem] = React.useState<number | null>(null);

  const getSeverityStyles = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-500/10',
          border: 'border-red-500/30',
          text: 'text-red-400',
          icon: <AlertTriangle className="w-5 h-5 text-red-400" />,
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-500/10',
          border: 'border-orange-500/30',
          text: 'text-orange-400',
          icon: <AlertTriangle className="w-5 h-5 text-orange-400" />,
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/30',
          text: 'text-amber-400',
          icon: <AlertCircle className="w-5 h-5 text-amber-400" />,
        };
      case 'LOW':
        return {
          bg: 'bg-blue-500/10',
          border: 'border-blue-500/30',
          text: 'text-blue-400',
          icon: <Info className="w-5 h-5 text-blue-400" />,
        };
      default:
        return {
          bg: 'bg-gray-500/10',
          border: 'border-gray-500/30',
          text: 'text-gray-400',
          icon: <Info className="w-5 h-5 text-gray-400" />,
        };
    }
  };

  const displayItems = items.slice(0, maxItems);

  if (items.length === 0) {
    return (
      <div className="glass-card p-6 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/20 mb-4">
          <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-white mb-2">No Issues Found</h3>
        <p className="text-gray-400">Great job! No security vulnerabilities detected.</p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-dark-700 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <span className="px-2 py-1 bg-dark-800 rounded text-sm text-gray-400">
          {items.length} {items.length === 1 ? 'issue' : 'issues'}
        </span>
      </div>

      {/* List */}
      <div className="divide-y divide-dark-800">
        {displayItems.map((item, index) => {
          const styles = getSeverityStyles(item.severity);
          const isExpanded = expandedItem === index;

          return (
            <div
              key={index}
              className={`${styles.bg} transition-all duration-200`}
            >
              <button
                onClick={() => setExpandedItem(isExpanded ? null : index)}
                className="w-full px-6 py-4 flex items-start gap-4 text-left hover:bg-white/5"
              >
                {/* Severity icon */}
                <div className="flex-shrink-0 mt-0.5">{styles.icon}</div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-sm font-medium ${styles.text}`}>
                      {item.severity}
                    </span>
                    {item.cwe && (
                      <span className="text-xs text-gray-500 bg-dark-800 px-2 py-0.5 rounded">
                        CWE-{String(item.cwe).replace(/[^0-9]/g, '')}
                      </span>
                    )}
                  </div>
                  <p className="text-white font-medium truncate">{item.title}</p>
                  {item.file && (
                    <div className="flex items-center gap-1 mt-1 text-sm text-gray-400">
                      <FileCode className="w-4 h-4" />
                      <span className="truncate">{item.file}</span>
                      {item.line && <span>:{item.line}</span>}
                    </div>
                  )}
                </div>

                {/* Expand icon */}
                <ChevronRight
                  className={`w-5 h-5 text-gray-400 transition-transform duration-200 flex-shrink-0
                            ${isExpanded ? 'rotate-90' : ''}`}
                />
              </button>

              {/* Expanded content */}
              {isExpanded && (
                <div className="px-6 pb-4 pl-16 space-y-3">
                  {item.description && (
                    <div>
                      <p className="text-sm text-gray-400">{item.description}</p>
                    </div>
                  )}
                  {item.recommendation && (
                    <div className="p-3 bg-dark-800/50 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">Recommendation</p>
                      <p className="text-sm text-gray-300">{item.recommendation}</p>
                    </div>
                  )}
                  {item.cwe && (
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        // Extract CWE number from various formats (CWE-798, 798, "CWE-798", etc.)
                        const cweStr = String(item.cwe);
                        const cweNum = cweStr.replace(/[^0-9]/g, '');
                        if (cweNum) {
                          window.open(
                            `https://cwe.mitre.org/data/definitions/${cweNum}.html`,
                            '_blank',
                            'noopener,noreferrer'
                          );
                        }
                      }}
                      className="inline-flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 cursor-pointer"
                    >
                      View CWE-{String(item.cwe).replace(/[^0-9]/g, '')} details
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Show more */}
      {items.length > maxItems && (
        <div className="px-6 py-3 border-t border-dark-700 text-center">
          <span className="text-sm text-gray-400">
            +{items.length - maxItems} more issues
          </span>
        </div>
      )}
    </div>
  );
};

export default RiskList;
