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
        // Slotio brand colors
        background: '#0A0E17',
        primary: '#00E5BD',
        accent: '#8B7CF5',
        'white-10': 'rgba(255, 255, 255, 0.1)',
        'white-5': 'rgba(255, 255, 255, 0.05)',
        // Legacy colors (for booking flow)
        pale: '#E8D9C4',
        gold: '#785D32', 
        rough: '#3E160C',
        darknavy: '#1A2847',
        bookedslot: '#D9CCC0',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      boxShadow: {
        'warm': '0 2px 8px rgba(62, 22, 12, 0.08)',
        'rough': '0 2px 4px rgba(62, 22, 12, 0.1)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}

export default config