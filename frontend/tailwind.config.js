/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#00d4ff',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        success: '#00ff88',
        danger: '#ff4d4d',
        warning: '#ffb800',
        dark: {
          900: '#0a0a1a',
          800: '#121830',
          700: '#1a1a2e',
          600: '#2a2a4a',
          500: '#3d3d5c',
          400: '#52527a',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-primary': 'linear-gradient(135deg, #00d4ff, #7b2cb8)',
        'gradient-success': 'linear-gradient(135deg, #00ff88, #00d4ff)',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)',
        'glow': '0 0 20px rgba(0, 212, 255, 0.3)',
        'glow-success': '0 0 20px rgba(0, 255, 136, 0.3)',
      }
    },
  },
  plugins: [],
}
