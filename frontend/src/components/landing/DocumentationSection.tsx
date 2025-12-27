import { Book, Code, Rocket, FileText, Download, ExternalLink } from 'lucide-react';

const docCategories = [
  {
    icon: Rocket,
    title: 'Getting Started',
    description: 'Quick setup guide and first steps',
    links: [
      { label: 'Installation', href: '#' },
      { label: 'Quick Start', href: '#' },
      { label: 'Basic Concepts', href: '#' },
    ]
  },
  {
    icon: Code,
    title: 'API Reference',
    description: 'Complete API documentation',
    links: [
      { label: 'Agent API', href: '#' },
      { label: 'Orchestrator API', href: '#' },
      { label: 'Utilities', href: '#' },
    ]
  },
  {
    icon: Book,
    title: 'Guides & Tutorials',
    description: 'In-depth guides and examples',
    links: [
      { label: 'Building Agents', href: '#' },
      { label: 'Multi-Agent Systems', href: '#' },
      { label: 'Best Practices', href: '#' },
    ]
  },
  {
    icon: FileText,
    title: 'Resources',
    description: 'Additional learning materials',
    links: [
      { label: 'Architecture Guide', href: '#' },
      { label: 'Security Model', href: '#' },
      { label: 'Performance Tuning', href: '#' },
    ]
  },
];

export default function DocumentationSection() {
  return (
    <section id="docs" className="py-20 px-6 bg-gray-50 dark:bg-gray-900/50">
      <div className="container-custom">
        <div className="section-header text-center">
          <h2 className="section-title">Documentation</h2>
          <p className="section-subtitle mx-auto">
            Comprehensive guides and references to help you build with AMAS
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {docCategories.map((category, index) => (
            <div
              key={category.title}
              className="card group animate-fadeInUp"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <category.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">{category.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{category.description}</p>
                </div>
              </div>
              <ul className="space-y-2">
                {category.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-primary-500 hover:text-primary-600 dark:hover:text-primary-400 flex items-center gap-2 group/link"
                    >
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover/link:opacity-100 transition-opacity" />
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="glass p-8 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Download className="w-6 h-6 text-primary-500" />
            <h3 className="text-xl font-bold">Download PDF Documentation</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-2xl mx-auto">
            Get the complete documentation as a PDF for offline reading and reference.
          </p>
          <button className="btn-primary">
            Download Documentation
          </button>
        </div>
      </div>
    </section>
  );
}