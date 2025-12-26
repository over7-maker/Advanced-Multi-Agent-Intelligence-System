import { useDarkMode } from '@/hooks/useDarkMode';
import Header from '@/components/landing/Header';
import HeroSection from '@/components/landing/HeroSection';
import ArchitectureSection from '@/components/landing/ArchitectureSection';
import FeaturesSection from '@/components/landing/FeaturesSection';
import MonitoringDashboard from '@/components/landing/MonitoringDashboard';
import InteractiveDemo from '@/components/landing/InteractiveDemo';
import DocumentationSection from '@/components/landing/DocumentationSection';
import Footer from '@/components/landing/Footer';

function App() {
  const { isDark, toggle } = useDarkMode();

  return (
    <div className={isDark ? 'dark' : ''}>
      <div className="min-h-screen bg-cream dark:bg-charcoal text-charcoal dark:text-gray-200 transition-colors duration-300">
        <Header isDark={isDark} onToggleDarkMode={toggle} />
        <main>
          <HeroSection />
          <ArchitectureSection />
          <FeaturesSection />
          <MonitoringDashboard />
          <InteractiveDemo />
          <DocumentationSection />
        </main>
        <Footer />
      </div>
    </div>
  );
}

export default App;
