/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        crypto: {
          green: '#00D4AA',
          red: '#FF6B6B',
          blue: '#4ECDC4',
          dark: '#1A1D29',
          gray: '#2D3748',
        }
      }
    },
  },
  plugins: [],
}
