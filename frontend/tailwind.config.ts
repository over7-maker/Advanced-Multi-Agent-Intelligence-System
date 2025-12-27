import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary': {
          50: '#f0f9fb',
          100: '#e0f3f7',
          200: '#b3e0e8',
          300: '#80cdd9',
          400: '#4dbacf',
          500: '#2180a5',
          600: '#1a6a87',
          700: '#14556e',
          800: '#0f4057',
          900: '#0a2b3c',
        },
        'secondary': {
          50: '#faf8f6',
          100: '#f5f1ed',
          200: '#e8dcd4',
          300: '#dcc7bb',
          400: '#d0b2a2',
          500: '#5e5240',
          600: '#544a38',
          700: '#4a4230',
          800: '#403a28',
          900: '#362f22',
        },
        'accent': {
          50: '#fef5f0',
          100: '#fdebe1',
          200: '#f9d4bb',
          300: '#f5bd95',
          400: '#f1a66f',
          500: '#a84b2f',
          600: '#963f28',
          700: '#843321',
          800: '#72271a',
          900: '#601b13',
        },
        'cream': '#fcf8f9',
        'charcoal': '#1f2121',
      },
      animation: {
        'pulse-ring': 'pulse-ring 2s infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-ring': {
          '0%': {
            transform: 'scale(1)',
            opacity: '1',
          },
          '100%': {
            transform: 'scale(1.5)',
            opacity: '0',
          },
        },
        'float': {
          '0%, 100%': {
            transform: 'translateY(0px)',
          },
          '50%': {
            transform: 'translateY(-20px)',
          },
        },
        'glow': {
          '0%, 100%': {
            opacity: '1',
          },
          '50%': {
            opacity: '0.5',
          },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

export default config
