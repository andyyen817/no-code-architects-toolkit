/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./test-pages/**/*.html",
    "./templates/**/*.html",
    "./static/**/*.js",
    "./design/prototypes/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#06b6d4',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
      },
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        'chinese': ['PingFang SC', 'Microsoft YaHei', 'sans-serif']
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
  darkMode: 'class'
}