import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pale: '#E8D9C4',
        gold: '#785D32', 
        rough: '#3E160C',
        darknavy: '#1A2847',
        bookedslot: '#D9CCC0',
      },
      boxShadow: {
        'warm': '0 2px 8px rgba(62, 22, 12, 0.08)',
        'rough': '0 2px 4px rgba(62, 22, 12, 0.1)',
      },
    },
  },
  plugins: [],
}

export default config