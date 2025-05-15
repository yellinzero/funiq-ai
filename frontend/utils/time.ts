import type { Locale } from '@/plugins/i18n/settings'
import dayjs from 'dayjs'

import relativeTime from 'dayjs/plugin/relativeTime'
import timezone from 'dayjs/plugin/timezone'
import utc from 'dayjs/plugin/utc'
import 'dayjs/locale/en'
import 'dayjs/locale/zh-cn'

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(relativeTime)

// Export dayjs instance for direct use
export const dayjsExtend = dayjs

// Default datetime format
const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'

// Time constants (in seconds)
export const OneMinute = 60
export const OneHour = OneMinute * 60
export const OneDay = OneHour * 24

/**
 * Checks if the given time value is invalid
 * @param {Date | string | number} time - Time value to check
 * @returns {boolean} True if time is invalid, false otherwise
 */
export function isInvalidTime(time: Date | string | number): boolean {
  return !time || !dayjs(time).isValid()
}

/**
 * Formats a time value using the specified format or default format
 * @param {Date | string} time - Time value to format
 * @param {string} [format] - Optional format string
 * @returns {string} Formatted time string
 */
export function formatTime(time: Date | string, format?: string): string {
  if (isInvalidTime(time))
    return time as string
  return dayjs(time).format(format || DATETIME_FORMAT)
}

/**
 * Sets the dayjs locale based on language code
 * @param {string} lang - Language code
 */
export function setDayJsLang(lang: Locale): void {
  dayjs.locale(lang === 'zh_CN' ? 'zh-cn' : 'en')
}

/**
 * Gets current time in specified format
 * @param {string} [format] - Optional format string
 * @returns {string} Formatted current time string
 */
export function getCurrentTime(format?: string): string {
  return dayjs().format(format || DATETIME_FORMAT)
}

/**
 * Gets current time in specified timezone
 * @param {string} tz - Timezone string
 * @param {string} [format] - Optional format string
 * @returns {string} Formatted current time string in specified timezone
 */
export function getCurrentTimeWithTimezone(tz: string, format?: string): string {
  return dayjs().tz(tz).format(format || DATETIME_FORMAT)
}

/**
 * Formats time with specified timezone
 * @param {Date | string} time - Time to format
 * @param {string} tz - Timezone string
 * @param {string} [format] - Optional format string
 * @returns {string} Formatted time string in specified timezone
 */
export function formatTimeWithTimezone(
  time: Date | string,
  tz: string,
  format?: string,
): string {
  if (isInvalidTime(time))
    return time as string
  return dayjs.tz(time, tz).format(format || DATETIME_FORMAT)
}

interface TimeConversionOptions {
  tz?: string
  format?: string
  type?: 'utc2local' | 'local2utc' | 'withTimezone'
}

/**
 * Converts time between different timezone formats
 * @param {Date | string | number} time - Time to convert
 * @param {TimeConversionOptions} [options] - Conversion options
 * @param {string} [options.tz] - Target timezone
 * @param {string} [options.format] - Output format
 * @param {('utc2local'|'local2utc'|'withTimezone')} [options.type] - Conversion type
 * @returns {string} Converted and formatted time string
 * @throws {Error} When timezone is required but not provided for 'withTimezone' type
 */
export function convertTime(
  time: Date | string | number,
  options: TimeConversionOptions = {},
): string {
  if (isInvalidTime(time))
    return time as string

  const { tz, format, type = 'utc2local' } = options

  let converted
  switch (type) {
    case 'utc2local':
      converted = dayjs.utc(time).local()
      break
    case 'local2utc':
      converted = dayjs(time).utc()
      break
    case 'withTimezone':
      if (!tz)
        throw new Error('Timezone is required for withTimezone conversion')
      converted = dayjs.tz(time, tz)
      break
  }

  return converted.format(format || DATETIME_FORMAT)
}

/**
 * Gets relative time from now (e.g., "3 hours ago")
 * @param {Date | string | number} time - Time to compare
 * @param {boolean} [withoutSuffix] - If true, returns without suffix
 * @returns {string} Relative time string
 */
export function getRelativeTime(
  time: Date | string | number,
  withoutSuffix?: boolean,
): string {
  if (isInvalidTime(time))
    return time as string
  return dayjs(time).fromNow(withoutSuffix)
}

/**
 * Gets duration between two times in seconds or milliseconds
 * @param {(string | number | Date | null)} [start] - Start time
 * @param {(string | number | Date | null)} [end] - End time
 * @param {boolean} [showMilliseconds] - If true, returns duration in milliseconds
 * @returns {number | undefined} Duration in seconds or milliseconds, undefined if invalid
 */
export function getDuration(
  start?: string | number | Date | null,
  end?: string | number | Date | null,
  showMilliseconds = false,
): number | undefined {
  if (!start || !end)
    return undefined

  try {
    const startTime = dayjs.utc(start).valueOf()
    const endTime = dayjs.utc(end).valueOf()
    const duration = Math.round((endTime - startTime) / 1000)

    if (duration < 0 && !showMilliseconds)
      return undefined
    return showMilliseconds ? endTime - startTime : duration
  }
  catch (error) {
    console.error(error)
    return undefined
  }
}

/**
 * Gets formatted duration with days, hours, minutes, and seconds
 * @param {(string | number | Date | null)} [start] - Start time
 * @param {(string | number | Date | null)} [end] - End time
 * @returns {{ days: number, hours: number, minutes: number, seconds: number } | undefined} Object containing the duration broken down into time units, or undefined if invalid
 */
export function getFormattedDuration(
  start?: string | number | Date | null,
  end?: string | number | Date | null,
) {
  try {
    let duration = getDuration(start, end)
    if ((!duration && duration !== 0) || duration < 0) {
      return
    }

    const days = Math.floor(duration / OneDay)
    duration %= OneDay

    const hours = Math.floor(duration / OneHour)
    duration %= OneHour

    const minutes = Math.floor(duration / OneMinute)
    const seconds = duration % OneMinute

    return {
      days,
      hours,
      minutes,
      seconds,
    }
  }
  catch (error) {
    console.error(error)
  }
}

/**
 * Gets date range from now
 * @param {number} days - Number of days to look back
 * @returns {[Dayjs, Dayjs]} Array containing start and end dates
 */
export function getDateRange(days: number) {
  const start = dayjs()
    .subtract(days - 1, 'day')
    .startOf('day')
  const end = dayjs().endOf('day')

  return [start, end]
}

/**
 * Compares two times and checks if first time is later than second time
 * @param {(string | number | Date)} time1 - First time to compare
 * @param {(string | number | Date)} time2 - Second time to compare
 * @returns {boolean} True if time1 is later than time2
 * @throws {Error} If either time is invalid
 */
export function isLaterThan(
  time1: string | number | Date,
  time2: string | number | Date,
): boolean {
  const date1 = dayjs(time1)
  const date2 = dayjs(time2)

  if (!date1.isValid() || !date2.isValid()) {
    throw new Error('Invalid time format')
  }

  return date1.isAfter(date2)
}
