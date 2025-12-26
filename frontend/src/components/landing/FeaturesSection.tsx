import { Shield, Zap, RefreshCw, Code, BarChart3, Lock } from 'lucide-react';

const features = [
  {
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-grade encryption, secure communication channels, and comprehensive audit logs for all agent activities.'
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Optimized for performance with sub-30ms latency. Handles thousands of concurrent agent interactions.'
  },
  {
    icon: RefreshCw,
    title: 'Self-Healing',
    description: 'Autonomous error recovery, automatic failover, and intelligent resource reallocation.'
  },
  {
    icon: Code,
    title: 'Developer Friendly',
    description: 'Clean Python API, comprehensive documentation, and extensive examples to get started quickly.'
  },
  {
    icon: BarChart3,
    title: 'Real-time Monitoring',
    description: 'Live dashboards, performance metrics, and detailed analytics for all your agent systems.'
  },
  {
    icon: Lock,
    title: 'Isolated Execution',
    description: 'Sandboxed agent environments with resource limits and strict security boundaries.'
  },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-20 px-6 bg-gray-50 dark:bg-gray-900/50">
      <div className="container-custom">
        <div className="section-header text-center">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle mx-auto">
            Everything you need to build production-ready multi-agent systems
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="card group card-hover glow-box animate-fadeInUp"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}