/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./*.html",
    "./templates/**/*.html",
    "./js/*.js",
    "./static/js/*.js",
    "./*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        primary: { 50: '#f0fdfa', 100: '#ccfbf1', 500: '#14b8a6', 600: '#0d9488', 700: '#0f766e' },
        accent:  { 500: '#8b5cf6', 600: '#7c3aed', 700: '#6d28d9' }
      },
      animation: {
        'float':        'float 6s ease-in-out infinite',
        'pulse-slow':   'pulse 4s cubic-bezier(0.4,0,0.6,1) infinite',
        'spin-slow':    'spin 8s linear infinite',
        'spin-reverse': 'spin-reverse 12s linear infinite',
        'orbit':        'orbit 6s linear infinite',
      },
      keyframes: {
        float:         { '0%,100%': { transform: 'translateY(0)' },     '50%': { transform: 'translateY(-10px)' } },
        'spin-reverse':{ '0%':      { transform: 'rotate(360deg)' },   '100%':{ transform: 'rotate(0deg)' } },
        'orbit':       { '0%':      { transform: 'rotate(0deg) translateX(60px) rotate(0deg)' },  '100%': { transform: 'rotate(360deg) translateX(60px) rotate(-360deg)' } },
      }
    },
  },
  plugins: [],
}
