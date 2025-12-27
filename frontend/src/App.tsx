import { useState } from 'react';
import HeroSection from './components/landing/HeroSection';
import ArchitectureSection from './components/landing/ArchitectureSection';
import FeaturesSection from './components/landing/FeaturesSection';
import MonitoringDashboard from './components/landing/MonitoringDashboard';
import InteractiveDemo from './components/landing/InteractiveDemo';
import CTASection from './components/landing/CTASection';
import Footer from './components/landing/Footer';
import Header from './components/landing/Header';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={darkMode ? 'dark' : 'light'}>
      <Header isDark={darkMode} onToggleDarkMode={toggleDarkMode} />
      <main>
        <HeroSection />
        <ArchitectureSection />
        <FeaturesSection />
        <MonitoringDashboard />
        <InteractiveDemo />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}

export default App;
