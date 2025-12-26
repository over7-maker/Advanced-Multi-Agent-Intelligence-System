import { Database, Brain, Network, Server, Shield, Activity } from 'lucide-react';

const architectureLayers = [
  {
    icon: Brain,
    name: 'Orchestration Layer',
    description: 'Intelligent task distribution and agent coordination',
    color: 'from-primary-500 to-primary-600'
  },
  {
    icon: Network,
    name: 'Communication Layer',
    description: 'Real-time message routing and event streaming',
    color: 'from-accent-500 to-accent-600'
  },
  {
    icon: Server,
    name: 'Execution Layer',
    description: 'Sandboxed agent runtime and resource management',
    color: 'from-secondary-500 to-secondary-600'
  },
  {
    icon: Database,
    name: 'Persistence Layer',
    description: 'State management and data storage',
    color: 'from-primary-400 to-primary-500'
  },
  {
    icon: Shield,
    name: 'Security Layer',
    description: 'Authentication, authorization, and encryption',
    color: 'from-accent-400 to-accent-500'
  },
  {
    icon: Activity,
    name: 'Monitoring Layer',
    description: 'Metrics collection and performance tracking',
    color: 'from-secondary-400 to-secondary-500'
  },
];

export default function ArchitectureSection() {
  return (
    <section id="architecture" className="py-20 px-6">
      <div className="container-custom">
        <div className="section-header text-center">
          <h2 className="section-title">Layered Architecture</h2>
          <p className="section-subtitle mx-auto">
            Built on a robust, modular architecture designed for scale and reliability
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {architectureLayers.map((layer, index) => (
            <div
              key={layer.name}
              className="card group relative overflow-hidden animate-fadeInUp"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${layer.color} opacity-10 rounded-full blur-2xl group-hover:opacity-20 transition-opacity`} />
              
              <div className="relative">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${layer.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <layer.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2">{layer.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{layer.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 glass p-8 rounded-2xl text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Each layer is independently scalable and can be deployed across multiple nodes for high availability.
          </p>
          <button className="btn-outline">
            View Architecture Details
          </button>
        </div>
      </div>
    </section>
  );
}