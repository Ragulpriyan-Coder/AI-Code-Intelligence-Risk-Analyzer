/**
 * Loading spinner and skeleton components.
 */
import React from 'react';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const Loader: React.FC<LoaderProps> = ({ size = 'md', text }) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`spinner ${sizeClasses[size]}`}></div>
      {text && <p className="text-gray-400 text-sm animate-pulse">{text}</p>}
    </div>
  );
};

export const FullPageLoader: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 bg-dark-950/90 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
          <div className="spinner w-16 h-16"></div>
          <div className="absolute inset-0 spinner w-16 h-16 opacity-30" style={{ animationDelay: '-0.5s' }}></div>
        </div>
        <p className="text-gray-300 text-lg">{text}</p>
      </div>
    </div>
  );
};

export const AnalyzingLoader: React.FC = () => {
  const [step, setStep] = React.useState(0);
  const steps = [
    'Cloning repository...',
    'Analyzing code structure...',
    'Running security scans...',
    'Calculating complexity metrics...',
    'Evaluating architecture...',
    'Computing scores...',
    'Generating insights...',
  ];

  React.useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-dark-950/95 backdrop-blur-md flex items-center justify-center z-50">
      <div className="flex flex-col items-center gap-8 max-w-md text-center px-4">
        {/* Animated logo */}
        <div className="relative">
          <div className="w-24 h-24 rounded-full bg-gradient-to-r from-primary-500 to-accent-500 animate-pulse-slow opacity-20 absolute inset-0"></div>
          <div className="w-24 h-24 rounded-full border-4 border-dark-700 border-t-primary-500 animate-spin"></div>
        </div>

        {/* Status text */}
        <div className="space-y-2">
          <p className="text-xl font-semibold text-white">{steps[step]}</p>
          <p className="text-gray-500 text-sm">This may take a moment</p>
        </div>

        {/* Progress dots */}
        <div className="flex gap-2">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i <= step ? 'bg-primary-500' : 'bg-dark-700'
              }`}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const SkeletonCard: React.FC = () => {
  return (
    <div className="glass-card p-6 animate-pulse">
      <div className="h-4 bg-dark-700 rounded w-1/3 mb-4"></div>
      <div className="h-12 bg-dark-700 rounded w-1/2 mb-2"></div>
      <div className="h-3 bg-dark-700 rounded w-2/3"></div>
    </div>
  );
};

export default Loader;
