// test example
import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useCountdown } from '../use-countdown'

describe('useCountdown', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('should initialize with countdown at 0', () => {
    const { result } = renderHook(() => useCountdown())
    expect(result.current.countdown).toBe(0)
  })

  it('should start countdown from specified duration', () => {
    const { result } = renderHook(() => useCountdown(10))

    act(() => {
      result.current.startCountdown()
    })

    expect(result.current.countdown).toBe(10)
  })

  it('should count down every second', () => {
    const { result } = renderHook(() => useCountdown(3))

    act(() => {
      result.current.startCountdown()
    })

    expect(result.current.countdown).toBe(3)

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(result.current.countdown).toBe(2)

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(result.current.countdown).toBe(1)

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(result.current.countdown).toBe(0)
  })

  it('should stop at 0 and not go negative', () => {
    const { result } = renderHook(() => useCountdown(1))

    act(() => {
      result.current.startCountdown()
    })

    act(() => {
      vi.advanceTimersByTime(2000) // Advance more than the duration
    })

    expect(result.current.countdown).toBe(0)
  })

  it('should use default duration of 60 seconds', () => {
    const { result } = renderHook(() => useCountdown())

    act(() => {
      result.current.startCountdown()
    })

    expect(result.current.countdown).toBe(60)
  })
})
