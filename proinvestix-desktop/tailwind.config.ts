import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        // ProInvestiX Brand Colors
        primary: {
          DEFAULT: '#C1272D', // Moroccan Red
          50: '#FDF2F2',
          100: '#FCE8E9',
          200: '#F8C9CB',
          300: '#F3A3A6',
          400: '#E85E63',
          500: '#C1272D',
          600: '#A91F24',
          700: '#8B191D',
          800: '#6E1417',
          900: '#5A1013',
          950: '#300809',
        },
        secondary: {
          DEFAULT: '#006233', // Moroccan Green
          50: '#E6F5EC',
          100: '#C1E6D1',
          200: '#98D4B3',
          300: '#6FC295',
          400: '#4DB17E',
          500: '#006233',
          600: '#00562D',
          700: '#004824',
          800: '#003A1C',
          900: '#002E16',
          950: '#001A0D',
        },
        accent: {
          DEFAULT: '#C58C2B', // Gold
          50: '#FCF7EE',
          100: '#F7EBD5',
          200: '#EFD7AB',
          300: '#E5BD75',
          400: '#D9A146',
          500: '#C58C2B',
          600: '#A57122',
          700: '#85581A',
          800: '#6A4615',
          900: '#573911',
          950: '#2E1E09',
        },
        // UI Colors
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-in-right': {
          from: { transform: 'translateX(100%)' },
          to: { transform: 'translateX(0)' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
