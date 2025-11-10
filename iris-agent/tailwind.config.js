/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
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
			fontFamily: {
				sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica Neue', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
			},
			colors: {
				// IRIS Brand Colors
				brand: {
					50: '#E6F0FF',
					100: '#CCE0FF',
					200: '#99BFFF',
					300: '#6699FF',
					400: '#3373FF',
					500: '#0066FF',
					600: '#0052CC',
					700: '#003D99',
					800: '#002966',
					900: '#001433',
					DEFAULT: '#0066FF',
				},
				// IRIS Neutral Colors
				neutral: {
					50: '#FAFAFA',
					100: '#F5F5F5',
					200: '#E5E5E5',
					300: '#D4D4D4',
					400: '#A3A3A3',
					500: '#A3A3A3',
					600: '#737373',
					700: '#404040',
					800: '#262626',
					900: '#171717',
					950: '#0A0A0A',
					DEFAULT: '#A3A3A3',
				},
				// IRIS Semantic Colors
				semantic: {
					success: '#10B981',
					warning: '#F59E0B',
					error: '#EF4444',
					info: '#3B82F6',
				},
				// Background Colors
				background: {
					light: {
						base: '#FAFAFA',
						surface: '#F5F5F5',
						raised: '#FFFFFF',
					},
					dark: {
						base: '#0A0A0A',
						surface: '#171717',
						raised: '#262626',
					},
				},
				// Text Colors
				text: {
					light: {
						primary: '#171717',
						secondary: '#404040',
						disabled: '#A3A3A3',
					},
					dark: {
						primary: '#FAFAFA',
						secondary: '#A3A3A3',
						disabled: '#525252',
					},
				},
				// Border Colors
				border: {
					light: {
						default: '#E5E5E5',
						subtle: '#F5F5F5',
					},
					dark: {
						default: '#262626',
						subtle: '#171717',
					},
				},
				// Shadcn/UI Colors (compatibility)
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: '#0066FF',
					foreground: 'hsl(var(--primary-foreground))',
				},
				secondary: {
					DEFAULT: '#F5F5F5',
					foreground: 'hsl(var(--secondary-foreground))',
				},
				accent: {
					DEFAULT: '#F5F5F5',
					foreground: 'hsl(var(--accent-foreground))',
				},
				destructive: {
					DEFAULT: '#EF4444',
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
			// IRIS Spacing (8pt Grid)
			spacing: {
				'xs': '8px',
				'sm': '12px',
				'md': '16px',
				'lg': '24px',
				'xl': '32px',
				'2xl': '40px',
				'3xl': '48px',
				'4xl': '64px',
				'5xl': '96px',
				'6xl': '128px',
			},
			// IRIS Border Radius
			borderRadius: {
				'sm': '8px',
				'md': '12px',
				'lg': '16px',
				'xl': '20px',
				'full': '9999px',
			},
			// IRIS Box Shadows
			boxShadow: {
				'card': '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
				'card-hover': '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',
				'modal': '0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)',
				'dropdown': '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
			},
			// IRIS Font Sizes
			fontSize: {
				'hero': '72px',
				'title': '48px',
				'subtitle': '32px',
				'body-large': '20px',
				'body': '16px',
				'body-small': '14px',
				'caption': '12px',
			},
			// IRIS Animation Duration
			animation: {
				'fast': '200ms',
				'normal': '250ms',
				'slow': '300ms',
			},
			// IRIS Transition Easing
			transitionTimingFunction: {
				'ease-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
				'ease-in-out': 'cubic-bezier(0.4, 0, 0.6, 1)',
			},
			// IRIS Component Sizes
			// Sidebar widths
			sidebar: {
				'collapsed': '64px',
				'expanded': '240px',
			},
			// Context panel widths
			'context-panel': {
				'collapsed': '48px',
				'expanded': '360px',
			},
			// Header height
			'header': '64px',
			// Button heights
			button: {
				'sm': '32px',
				'md': '40px',
				'lg': '48px',
			},
			// Input heights
			input: {
				'md': '40px',
				'lg': '48px',
			},
			// Card padding
			card: {
				'sm': '24px',
				'md': '32px',
				'lg': '40px',
			},
			// Avatar sizes
			avatar: {
				'sm': '24px',
				'md': '32px',
				'lg': '40px',
				'xl': '48px',
			},
			// Icon sizes
			icon: {
				'sm': '16px',
				'md': '20px',
				'lg': '24px',
			},
			keyframes: {
				'accordion-down': {
					from: { height: 0 },
					to: { height: 'var(--radix-accordion-content-height)' },
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: 0 },
				},
				'pulse-stream': {
					'0%, 100%': { opacity: 0.6, transform: 'scale(0.8)' },
					'50%': { opacity: 1, transform: 'scale(1.2)' },
				},
				'slide-in-right': {
					'0%': { transform: 'translateX(100%)', opacity: 0 },
					'100%': { transform: 'translateX(0)', opacity: 1 },
				},
				'fade-in-up': {
					'0%': { transform: 'translateY(20px)', opacity: 0 },
					'100%': { transform: 'translateY(0)', opacity: 1 },
				},
				'shimmer': {
					'0%': { backgroundPosition: '-200% 0' },
					'100%': { backgroundPosition: '200% 0' },
				},
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'pulse-stream': 'pulse-stream 600ms infinite',
				'slide-in-right': 'slide-in-right 300ms ease-out',
				'fade-in-up': 'fade-in-up 300ms ease-out',
				'shimmer': 'shimmer 2000ms infinite ease-in-out',
			},
		},
	},
	plugins: [require('tailwindcss-animate')],
}