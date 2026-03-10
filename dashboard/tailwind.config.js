/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'eco-bg': '#0f172a',
        'eco-card': '#1e293b',
        'eco-text': '#e2e8f0',
        'eco-green': '#22c55e',
        'eco-yellow': '#eab308',
        'eco-red': '#ef4444',
        'eco-solar': '#fbbf24',
        'eco-wind': '#38bdf8',
        'eco-rain': '#60a5fa',
      },
    },
  },
  plugins: [],
};
