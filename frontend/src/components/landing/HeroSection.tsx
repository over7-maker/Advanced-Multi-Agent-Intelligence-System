import { ArrowRight, Sparkles } from 'lucide-react';

export default function HeroSection() {
  return (
    <section id="hero" className="pt-32 pb-20 px-6">
      <div className="container-custom">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-fadeInUp">
            <Sparkles className="w-4 h-4 text-accent-500" />
            <span className="text-sm font-medium">Production-Ready Multi-Agent Framework</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-hero mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
            Build{' '}
            <span className="gradient-text">Intelligent Agent Systems</span>{' '}
            That Evolve
          </h1>

          {/* Subheadline */}
          <p className="text-responsive text-gray-600 dark:text-gray-400 mb-10 max-w-2xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            AMAS is a comprehensive orchestration framework for building autonomous, 
            self-improving AI agents. Deploy scalable multi-agent systems with confidence.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <button className="btn-primary flex items-center justify-center gap-2">
              Start Building
              <ArrowRight className="w-4 h-4" />
            </button>
            <button className="btn-outline">
              View Documentation
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-500 mb-1">99.97%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-accent-500 mb-1">12+</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-500 mb-1">1.8K+</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Tasks Completed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-accent-500 mb-1">23ms</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Avg Latency</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}