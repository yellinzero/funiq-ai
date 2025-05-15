import type { Config } from 'tailwindcss'
import tailwindMulti from 'tailwindcss-multi'

module.exports = {
  theme: {
    extend: {
      keyframes: {
        'caret-blink': {
          '0%,70%,100%': { opacity: '1' },
          '20%,50%': { opacity: '0' },
        },
      },
      animation: {
        'caret-blink': 'caret-blink 1.25s ease-out infinite',
      },
    },
  },
  plugins: [
    tailwindMulti,
  ],
} satisfies Config
