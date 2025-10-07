/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'neural-blue': '#0EA5E9',
        'quantum-violet': '#6366F1', 
        'emergence-gold': '#F59E0B',
        'deep-space': '#0F172A',
        'cosmic-silver': '#E2E8F0'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #3b82f6, 0 0 10px #3b82f6, 0 0 15px #3b82f6' },
          '100%': { boxShadow: '0 0 10px #3b82f6, 0 0 20px #3b82f6, 0 0 30px #3b82f6' },
        }
      },
      backdropBlur: {
        'xs': '2px',
      },
      fontFamily: {
        'neural': ['Inter', 'system-ui', 'sans-serif'],
        'code': ['JetBrains Mono', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}