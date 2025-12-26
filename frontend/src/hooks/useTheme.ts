/**
 * Dark Mode Theme Hook
 * Manages light/dark theme switching with localStorage persistence
 */

import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark';

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>('light');
  const [isMounted, setIsMounted] = useState(false);

  // Initialize theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme: Theme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    setTheme(initialTheme);
    applyTheme(initialTheme);
    setIsMounted(true);
  }, []);

  // Apply theme to document
  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement;
    root.setAttribute('data-color-scheme', newTheme);
    root.style.colorScheme = newTheme;
    localStorage.setItem('theme', newTheme);
  };

  // Toggle between light and dark
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  return {
    theme,
    setTheme: (newTheme: Theme) => {
      setTheme(newTheme);
      applyTheme(newTheme);
    },
    toggleTheme,
    isMounted,
  };
};

export type { Theme };
