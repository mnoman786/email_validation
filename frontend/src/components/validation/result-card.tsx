'use client'

import { ValidationResult } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from '@/components/ui/badge'
import { cn, getScoreColor, getScoreGradient, getActionLabel, getActionColor, formatDateTime } from '@/lib/utils'
import {
  CheckCircle2, XCircle, AlertCircle, Globe, Server, Shield,
  Mail, Clock, Zap, Info
} from 'lucide-react'

interface ResultCardProps {
  result: ValidationResult
}

function BooleanIndicator({ value, trueLabel, falseLabel }: { value: boolean; trueLabel: string; falseLabel: string }) {
  return (
    <div className="flex items-center gap-1.5">
      {value
        ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
        : <XCircle className="w-3.5 h-3.5 text-red-400" />}
      <span className={cn('text-xs font-medium', value ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400')}>
        {value ? trueLabel : falseLabel}
      </span>
    </div>
  )
}

export function ValidationResultCard({ result }: ResultCardProps) {
  const scoreOffset = 283 - (283 * result.score) / 100

  return (
    <Card className="animate-slide-up">
      <CardContent className="pt-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-6 pb-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3 flex-1">
            <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <Mail className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </div>
            <div>
              <p className="font-semibold text-gray-900 dark:text-white text-lg">{result.email}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {result.domain} &bull; {result.processing_time_ms}ms
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <StatusBadge status={result.status} />

            {/* Score circle */}
            <div className="relative w-16 h-16">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r="45"
                  fill="none"
                  strokeWidth="8"
                  strokeLinecap="round"
                  stroke="url(#scoreGrad)"
                  strokeDasharray="283"
                  strokeDashoffset={scoreOffset}
                  className="transition-all duration-1000"
                />
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={cn('text-sm font-bold', getScoreColor(result.score))}>{result.score}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Checks Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
          <CheckItem icon={<Shield className="w-4 h-4" />} label="Syntax" value={result.syntax_valid} />
          <CheckItem icon={<Globe className="w-4 h-4" />} label="DNS Valid" value={result.dns_valid} />
          <CheckItem icon={<Server className="w-4 h-4" />} label="MX Records" value={result.mx_found} />
          <CheckItem icon={<Zap className="w-4 h-4" />} label="SMTP Check" value={result.smtp_check} />
          <CheckItem icon={<XCircle className="w-4 h-4" />} label="Not Disposable" value={!result.is_disposable} />
          <CheckItem icon={<AlertCircle className="w-4 h-4" />} label="Not Spam Trap" value={!result.is_spam_trap} />
          <CheckItem icon={<Info className="w-4 h-4" />} label="Not Catch-All" value={!result.is_catch_all} />
          <CheckItem icon={<Mail className="w-4 h-4" />} label="Not Role Account" value={!result.is_role_account} />
        </div>

        {/* Details Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <Detail label="Domain Reputation" value={result.domain_reputation} capitalize />
          <Detail label="Risk Level" value={result.risk_level} capitalize />
          <Detail label="Free Provider" value={result.is_free_provider ? 'Yes' : 'No'} />
          <Detail
            label="Suggested Action"
            value={getActionLabel(result.suggested_action)}
            className={getActionColor(result.suggested_action)}
          />
        </div>

        {/* MX Records */}
        {(result.mx_records ?? []).length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">MX Records</p>
            <div className="flex flex-wrap gap-2">
              {(result.mx_records ?? []).slice(0, 3).map((mx) => (
                <span key={mx} className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono text-gray-700 dark:text-gray-300">
                  {mx}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Score Breakdown */}
        {result.score_breakdown && Object.keys(result.score_breakdown ?? {}).length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3">Score Breakdown</p>
            <div className="space-y-2">
              {Object.entries(result.score_breakdown ?? {})
                .filter(([key]) => key !== 'total')
                .map(([key, data]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-xs text-gray-600 dark:text-gray-400">{data.label}</span>
                    <span className={cn('text-xs font-semibold', data.points >= 0 ? 'text-emerald-600' : 'text-red-500')}>
                      {data.points >= 0 ? '+' : ''}{data.points}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function CheckItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: boolean }) {
  return (
    <div className={cn(
      'flex items-center gap-2 p-3 rounded-lg border',
      value
        ? 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-100 dark:border-emerald-900'
        : 'bg-red-50 dark:bg-red-950/50 border-red-100 dark:border-red-900'
    )}>
      <span className={cn('w-4 h-4', value ? 'text-emerald-500' : 'text-red-400')}>{icon}</span>
      <span className={cn('text-xs font-medium', value ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-600 dark:text-red-400')}>
        {label}
      </span>
    </div>
  )
}

function Detail({ label, value, capitalize, className }: {
  label: string; value: string; capitalize?: boolean; className?: string
}) {
  return (
    <div>
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className={cn('text-sm font-semibold text-gray-900 dark:text-white mt-0.5', capitalize && 'capitalize', className)}>
        {value}
      </p>
    </div>
  )
}
