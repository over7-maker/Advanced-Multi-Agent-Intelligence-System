import { Github, Twitter, Linkedin, Mail } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-12 px-6">
      <div className="container-custom">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                <span className="text-sm font-bold text-white">A</span>
              </div>
              <span className="font-bold text-lg">AMAS</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Building the future of autonomous agent systems.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="mailto:contact@amas.ai"
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              <li><a href="#features" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Features</a></li>
              <li><a href="#architecture" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Architecture</a></li>
              <li><a href="#monitoring" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Monitoring</a></li>
              <li><a href="#demo" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Demo</a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><a href="#docs" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Documentation</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">API Reference</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Tutorials</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Examples</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">About</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Blog</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Careers</a></li>
              <li><a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Contact</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-gray-200 dark:border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            © {currentYear} AMAS. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Privacy Policy</a>
            <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Terms of Service</a>
            <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-colors">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
}