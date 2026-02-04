/**
 * Landing page component.
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Code, Boxes, AlertTriangle, Zap, Lock, FileText, ArrowRight } from 'lucide-react';
import Navbar from '../components/Navbar';

const Landing: React.FC = () => {
  const features = [
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Security Analysis',
      description: 'Detect vulnerabilities, insecure patterns, and potential exploits with CWE mapping.',
      color: 'text-red-400',
      bg: 'bg-red-500/10',
    },
    {
      icon: <Code className="w-8 h-8" />,
      title: 'Code Quality',
      description: 'Measure complexity, maintainability index, and identify code smells.',
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
    },
    {
      icon: <Boxes className="w-8 h-8" />,
      title: 'Architecture Review',
      description: 'Analyze dependencies, detect circular imports, and assess modularity.',
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
    },
    {
      icon: <AlertTriangle className="w-8 h-8" />,
      title: 'Tech Debt Tracking',
      description: 'Quantify technical debt and prioritize refactoring efforts.',
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
    },
  ];

  const benefits = [
    { icon: <Zap className="w-5 h-5" />, text: 'Fast static analysis' },
    { icon: <Lock className="w-5 h-5" />, text: 'No code stored' },
    { icon: <FileText className="w-5 h-5" />, text: 'PDF reports' },
  ];

  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/30
                        rounded-full text-primary-400 text-sm font-medium mb-8">
            <Shield className="w-4 h-4" />
            AI-Powered Code Governance
          </div>

          {/* Headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="text-white">Analyze Code Quality,</span>
            <br />
            <span className="text-gradient">Security & Risk</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            Get instant insights into your codebase health. Detect vulnerabilities, measure
            complexity, and track technical debt with deterministic scoring.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-glow text-lg flex items-center gap-2">
              Get Started Free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="btn-secondary text-lg">
              Sign In
            </Link>
          </div>

          {/* Benefits */}
          <div className="flex flex-wrap items-center justify-center gap-6 mt-12">
            {benefits.map((benefit, i) => (
              <div key={i} className="flex items-center gap-2 text-gray-400">
                <span className="text-primary-400">{benefit.icon}</span>
                <span>{benefit.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Comprehensive Code Intelligence
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Rule-based analysis with deterministic scoring. AI explains results, never makes decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="glass-card p-8 transition-all duration-300 hover:scale-[1.02] hover:shadow-glow"
              >
                <div className={`inline-flex p-3 rounded-xl ${feature.bg} ${feature.color} mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How It Works
            </h2>
          </div>

          <div className="space-y-8">
            {[
              { step: '1', title: 'Enter Repository URL', desc: 'Paste your public GitHub repository URL' },
              { step: '2', title: 'Automated Analysis', desc: 'Static analysis runs on your code (no code stored)' },
              { step: '3', title: 'Review Results', desc: 'Get scores, risks, and AI-powered explanations' },
              { step: '4', title: 'Download Report', desc: 'Export professional PDF report for your team' },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-6">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-500/20 border border-primary-500/30
                              flex items-center justify-center text-primary-400 font-bold text-lg">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-1">{item.title}</h3>
                  <p className="text-gray-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="glass-card p-12 gradient-border">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Analyze Your Code?
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Start for free. No credit card required. Get insights in minutes.
            </p>
            <Link to="/signup" className="btn-glow text-lg inline-flex items-center gap-2">
              Start Analyzing
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-dark-800">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          <p>AI Code Intelligence & Risk Analyzer</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
