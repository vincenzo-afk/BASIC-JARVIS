module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./public/index.html"
    ],
    theme: {
        extend: {
            colors: {
                jarvis: {
                    cyan: '#22d3ee',
                    blue: '#3b82f6',
                    dark: '#0a0a0a',
                    gray: '#1a1a1a'
                }
            },
            animation: {
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'float': 'float 3s ease-in-out infinite'
            },
            keyframes: {
                'pulse-glow': {
                    '0%, 100%': { opacity: 1, boxShadow: '0 0 20px rgba(34, 211, 238, 0.5)' },
                    '50%': { opacity: 0.8, boxShadow: '0 0 40px rgba(34, 211, 238, 0.8)' }
                },
                'float': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' }
                }
            }
        }
    },
    plugins: []
}
