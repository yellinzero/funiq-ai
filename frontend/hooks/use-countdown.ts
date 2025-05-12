import { useCallback, useState } from 'react'

export function useCountdown(duration = 60) {
  const [countdown, setCountdown] = useState(0)

  const startCountdown = useCallback(() => {
    setCountdown(duration)
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }, [duration])

  return {
    countdown,
    startCountdown,
  }
}
