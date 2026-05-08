import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { ValidationStatus, RiskLevel } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toString()
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s`
  return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
}

export const STATUS_COLORS: Record<ValidationStatus, string> = {
  valid: 'text-emerald-600 bg-emerald-50 border-emerald-200 dark:text-emerald-400 dark:bg-emerald-950 dark:border-emerald-800',
  invalid: 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-950 dark:border-red-800',
  risky: 'text-amber-600 bg-amber-50 border-amber-200 dark:text-amber-400 dark:bg-amber-950 dark:border-amber-800',
  disposable: 'text-purple-600 bg-purple-50 border-purple-200 dark:text-purple-400 dark:bg-purple-950 dark:border-purple-800',
  spam_trap: 'text-rose-600 bg-rose-50 border-rose-200 dark:text-rose-400 dark:bg-rose-950 dark:border-rose-800',
  catch_all: 'text-blue-600 bg-blue-50 border-blue-200 dark:text-blue-400 dark:bg-blue-950 dark:border-blue-800',
  unknown: 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-900 dark:border-gray-700',
}

export const STATUS_LABELS: Record<ValidationStatus, string> = {
  valid: 'Valid',
  invalid: 'Invalid',
  risky: 'Risky',
  disposable: 'Disposable',
  spam_trap: 'Spam Trap',
  catch_all: 'Catch-All',
  unknown: 'Unknown',
}

export const RISK_COLORS: Record<RiskLevel, string> = {
  low: 'text-emerald-600',
  medium: 'text-amber-600',
  high: 'text-orange-600',
  critical: 'text-red-600',
}

export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-amber-600'
  if (score >= 30) return 'text-orange-600'
  return 'text-red-600'
}

export function getScoreGradient(score: number): string {
  if (score >= 80) return 'from-emerald-500 to-green-400'
  if (score >= 60) return 'from-amber-500 to-yellow-400'
  if (score >= 30) return 'from-orange-500 to-amber-400'
  return 'from-red-500 to-rose-400'
}

export function getActionColor(action: string): string {
  switch (action) {
    case 'safe_to_send': return 'text-emerald-600'
    case 'send_with_caution': return 'text-amber-600'
    case 'do_not_send': return 'text-red-600'
    default: return 'text-gray-500'
  }
}

export function getActionLabel(action: string): string {
  switch (action) {
    case 'safe_to_send': return 'Safe to Send'
    case 'send_with_caution': return 'Send with Caution'
    case 'do_not_send': return 'Do Not Send'
    default: return 'Unknown'
  }
}
