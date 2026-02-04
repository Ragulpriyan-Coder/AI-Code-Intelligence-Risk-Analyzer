/**
 * Repository input form for analysis.
 */
import React, { useState } from 'react';
import { Github, GitBranch, Search, AlertCircle } from 'lucide-react';

interface RepoFormProps {
  onSubmit: (repoUrl: string, branch: string) => void;
  isLoading?: boolean;
}

const RepoForm: React.FC<RepoFormProps> = ({ onSubmit, isLoading = false }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const validateGitHubUrl = (url: string): boolean => {
    const patterns = [
      /^https?:\/\/github\.com\/[^/]+\/[^/]+\/?$/,
      /^https?:\/\/github\.com\/[^/]+\/[^/]+\.git$/,
      /^github\.com\/[^/]+\/[^/]+\/?$/,
    ];
    return patterns.some((pattern) => pattern.test(url.trim()));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    if (!validateGitHubUrl(repoUrl)) {
      setError('Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)');
      return;
    }

    onSubmit(repoUrl.trim(), branch.trim() || 'main');
  };

  // Example repos for quick testing
  const exampleRepos = [
    { name: 'Flask', url: 'https://github.com/pallets/flask' },
    { name: 'FastAPI', url: 'https://github.com/tiangolo/fastapi' },
    { name: 'Requests', url: 'https://github.com/psf/requests' },
  ];

  return (
    <div className="glass-card p-6 md:p-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 rounded-xl bg-primary-500/20">
          <Github className="w-6 h-6 text-primary-400" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-white">Analyze Repository</h2>
          <p className="text-sm text-gray-400">Enter a public GitHub repository URL</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Repository URL input */}
        <div>
          <label htmlFor="repoUrl" className="block text-sm font-medium text-gray-300 mb-2">
            Repository URL
          </label>
          <div className="relative">
            <input
              type="text"
              id="repoUrl"
              value={repoUrl}
              onChange={(e) => {
                setRepoUrl(e.target.value);
                setError(null);
              }}
              placeholder="https://github.com/owner/repository"
              className="input-field pl-10"
              disabled={isLoading}
            />
            <Github className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          </div>
        </div>

        {/* Advanced options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-gray-400 hover:text-gray-300 flex items-center gap-1"
          >
            <GitBranch className="w-4 h-4" />
            {showAdvanced ? 'Hide' : 'Show'} advanced options
          </button>

          {showAdvanced && (
            <div className="mt-3">
              <label htmlFor="branch" className="block text-sm font-medium text-gray-300 mb-2">
                Branch
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="branch"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  className="input-field pl-10"
                  disabled={isLoading}
                />
                <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              </div>
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full btn-glow flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="spinner w-5 h-5"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Analyze Repository</span>
            </>
          )}
        </button>
      </form>

      {/* Quick examples */}
      <div className="mt-6 pt-6 border-t border-dark-700">
        <p className="text-sm text-gray-500 mb-3">Try an example:</p>
        <div className="flex flex-wrap gap-2">
          {exampleRepos.map((repo) => (
            <button
              key={repo.name}
              type="button"
              onClick={() => setRepoUrl(repo.url)}
              disabled={isLoading}
              className="px-3 py-1.5 bg-dark-800 hover:bg-dark-700 text-gray-300 text-sm
                       rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
              {repo.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RepoForm;
