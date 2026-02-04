/**
 * Main dashboard page for code analysis.
 */
import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Clock,
  Files,
  Code,
  History,
  Trash2,
  RefreshCw,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import RepoForm from '../components/RepoForm';
import ScoreCard, { UrgencyBadge } from '../components/ScoreCard';
import RiskList from '../components/RiskList';
import { AnalyzingLoader } from '../components/Loader';
import {
  analysisService,
  reportService,
  AnalysisResult,
  AnalysisListItem,
} from '../services/api';
import { AxiosError } from 'axios';
import { ApiError } from '../services/api';

const Dashboard: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Load analysis history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await analysisService.listAnalyses();
      setAnalysisHistory(history);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleAnalyze = async (repoUrl: string, branch: string) => {
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await analysisService.analyzeRepo({ repo_url: repoUrl, branch });
      setAnalysisResult(result);
      loadHistory(); // Refresh history
    } catch (err) {
      const axiosError = err as AxiosError<ApiError>;
      setError(axiosError.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!analysisResult) return;

    setIsDownloading(true);
    try {
      await reportService.downloadPdfWithFilename(analysisResult.id, analysisResult.repo_name);
    } catch (err) {
      console.error('PDF download failed:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleLoadAnalysis = async (id: number) => {
    try {
      const result = await analysisService.getAnalysis(id);
      setAnalysisResult(result);
      setShowHistory(false);
      setError(null);
    } catch (err) {
      console.error('Failed to load analysis:', err);
    }
  };

  const handleDeleteAnalysis = async (id: number) => {
    try {
      await analysisService.deleteAnalysis(id);
      loadHistory();
      if (analysisResult?.id === id) {
        setAnalysisResult(null);
      }
    } catch (err) {
      console.error('Failed to delete analysis:', err);
    }
  };

  // Extract security issues from metrics
  const getSecurityIssues = () => {
    if (!analysisResult?.metrics?.security) return [];
    const security = analysisResult.metrics.security as Record<string, unknown>;
    return (security.top_issues as Array<Record<string, unknown>>) || [];
  };

  return (
    <div className="min-h-screen pb-20">
      <Navbar />

      {/* Analyzing overlay */}
      {isAnalyzing && <AnalyzingLoader />}

      <main className="pt-24 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
              <p className="text-gray-400">Analyze GitHub repositories for code quality and security</p>
            </div>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="btn-secondary flex items-center gap-2"
            >
              <History className="w-5 h-5" />
              {showHistory ? 'New Analysis' : 'View History'}
            </button>
          </div>

          {/* History View */}
          {showHistory ? (
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold text-white mb-6">Analysis History</h2>
              {analysisHistory.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No analyses yet. Start by analyzing a repository.</p>
              ) : (
                <div className="space-y-4">
                  {analysisHistory.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-4 bg-dark-800/50 rounded-xl
                               hover:bg-dark-800 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-white truncate">{item.repo_name}</h3>
                        <p className="text-sm text-gray-400">
                          {new Date(item.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="hidden sm:flex items-center gap-3">
                          <span className="text-sm">
                            <span className="text-gray-500">Sec:</span>{' '}
                            <span className="text-white">{item.security_score.toFixed(0)}</span>
                          </span>
                          <UrgencyBadge urgency={item.refactor_urgency} size="sm" />
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleLoadAnalysis(item.id)}
                            className="p-2 text-gray-400 hover:text-primary-400 transition-colors"
                            title="View"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteAnalysis(item.id)}
                            className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <>
              {/* Analysis Form */}
              {!analysisResult && (
                <div className="max-w-2xl mx-auto mb-12">
                  <RepoForm onSubmit={handleAnalyze} isLoading={isAnalyzing} />
                  {error && (
                    <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
                      {error}
                    </div>
                  )}
                </div>
              )}

              {/* Analysis Results */}
              {analysisResult && (
                <div className="space-y-8">
                  {/* Result Header */}
                  <div className="glass-card p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">{analysisResult.repo_name}</h2>
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Files className="w-4 h-4" />
                          {analysisResult.files_analyzed} files
                        </span>
                        <span className="flex items-center gap-1">
                          <Code className="w-4 h-4" />
                          {analysisResult.total_lines.toLocaleString()} lines
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {analysisResult.analysis_duration_seconds.toFixed(1)}s
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={handleDownloadPdf}
                        disabled={isDownloading}
                        className="btn-glow flex items-center gap-2"
                      >
                        {isDownloading ? (
                          <>
                            <div className="spinner w-5 h-5"></div>
                            Generating...
                          </>
                        ) : (
                          <>
                            <Download className="w-5 h-5" />
                            Download PDF
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => setAnalysisResult(null)}
                        className="btn-secondary"
                      >
                        New Analysis
                      </button>
                    </div>
                  </div>

                  {/* Score Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <ScoreCard
                      title="Security Score"
                      score={analysisResult.scores.security_score}
                      type="security"
                      subtitle="Vulnerability assessment"
                    />
                    <ScoreCard
                      title="Maintainability"
                      score={analysisResult.scores.maintainability_score}
                      type="maintainability"
                      subtitle="Code quality metrics"
                    />
                    <ScoreCard
                      title="Architecture"
                      score={analysisResult.scores.architecture_score}
                      type="architecture"
                      subtitle="Structure assessment"
                    />
                    <ScoreCard
                      title="Tech Debt Index"
                      score={analysisResult.scores.tech_debt_index}
                      type="debt"
                      subtitle={`Urgency: ${analysisResult.scores.refactor_urgency}`}
                    />
                  </div>

                  {/* Urgency Banner */}
                  {(analysisResult.scores.refactor_urgency === 'High' ||
                    analysisResult.scores.refactor_urgency === 'Critical') && (
                    <div
                      className={`p-4 rounded-xl border ${
                        analysisResult.scores.refactor_urgency === 'Critical'
                          ? 'bg-red-500/10 border-red-500/30'
                          : 'bg-orange-500/10 border-orange-500/30'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <UrgencyBadge urgency={analysisResult.scores.refactor_urgency} size="lg" />
                        <p className="text-gray-300">
                          {analysisResult.scores.refactor_urgency === 'Critical'
                            ? 'Immediate attention required. Critical issues detected.'
                            : 'Significant issues found. Plan refactoring soon.'}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Two Column Layout */}
                  <div className="grid lg:grid-cols-2 gap-8">
                    {/* Security Issues */}
                    <RiskList items={getSecurityIssues()} title="Security Issues" maxItems={8} />

                    {/* AI Explanation */}
                    <div className="glass-card p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <FileText className="w-5 h-5 text-primary-400" />
                        <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
                      </div>
                      <div className="prose prose-invert prose-sm max-w-none">
                        {analysisResult.llm_explanation.split('\n').map((line, i) => {
                          if (line.startsWith('## ')) {
                            return (
                              <h4 key={i} className="text-primary-400 font-semibold mt-4 mb-2">
                                {line.replace('## ', '')}
                              </h4>
                            );
                          }
                          if (line.startsWith('- ') || line.startsWith('* ')) {
                            return (
                              <p key={i} className="text-gray-300 ml-4 my-1">
                                • {line.slice(2)}
                              </p>
                            );
                          }
                          if (line.match(/^\d+\./)) {
                            return (
                              <p key={i} className="text-gray-300 ml-4 my-1">
                                {line}
                              </p>
                            );
                          }
                          if (line.trim() === '' || line.startsWith('#') || line.startsWith('---')) {
                            return null;
                          }
                          return (
                            <p key={i} className="text-gray-300 my-2">
                              {line.replace(/\*\*/g, '')}
                            </p>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
