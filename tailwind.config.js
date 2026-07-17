/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';
import themes from 'daisyui/src/theming/themes.js';

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#7c3aed',
        accent: '#a78bfa',
      },
      fontFamily: {
        sans: [
          'Nunito',
          'PingFang SC',
          'Hiragino Sans GB',
          'Microsoft YaHei',
          'system-ui',
          'sans-serif',
        ],
      },
      maxWidth: {
        content: '1200px',
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        dark: {
          ...themes['dark'],
          'color-scheme': 'dark',
          primary: '#7c3aed',
          'primary-content': '#ffffff',
          secondary: '#a78bfa',
          'secondary-content': '#1c1425',
          accent: '#a78bfa',
          'accent-content': '#1c1425',
          neutral: '#1a1a1f',
          'neutral-content': '#a8a29e',
          'base-100': '#0d0d10',
          'base-200': '#161619',
          'base-300': '#232329',
          'base-content': '#f5f5f4',
          info: '#60a5fa',
          success: '#34d399',
          warning: '#fbbf24',
          error: '#f87171',
          '--rounded-box': '0.5rem',
          '--rounded-btn': '0.25rem',
          '--rounded-badge': '0.25rem',
          '--border-btn': '1px',
          '--tab-radius': '0.25rem',
        },
      },
    ],
    darkTheme: 'dark',
    base: true,
    styled: true,
    utils: true,
  },
};
