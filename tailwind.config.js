/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';
import daisyuiThemes from 'daisyui/src/theming/themes';

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0066cc',
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        dark: {
          ...daisyuiThemes['dark'],
          primary: '#0066cc',
          'primary-focus': '#0052a3',
        },
      },
    ],
    darkTheme: 'dark',
    base: true,
    styled: true,
    utils: true,
  },
};
