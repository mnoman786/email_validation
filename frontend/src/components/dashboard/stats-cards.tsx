'use client'

import { ValidationStats } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { cn, formatNumber } from '@/lib/utils'
import { TrendingUp, TrendingDown, Mail, CheckCircle, XCircle, AlertTriangle, Trash2, ShieldAlert, HelpCircle } from 'lucide-react'

interface StatsCardsProps {
  stats: ValidationStats['overview']
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      label: 'Total Validated',
      value: stats.total_validations,
      icon: Mail,
      color: 'text-blue-600',
      bg: 'bg-blue-50 dark:bg-blue-950',
      border: 'border-blue-100 dark:border-blue-900',
    },
    {
      label: 'Valid Emails',
      value: stats.valid_count,
      pct: stats.valid_percentage,
      icon: CheckCircle,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50 dark:bg-emerald-950',
      border: 'border-emerald-100 dark:border-emerald-900',
    },
    {
      label: 'Invalid Emails',
      value: stats.invalid_count,
      pct: stats.total_validations ? Math.round((stats.invalid_count / stats.total_validations) * 100) : 0,
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50 dark:bg-red-950',
      border: 'border-red-100 dark:border-red-900',
    },
    {
      label: 'Risky Emails',
      value: stats.risky_count,
      pct: stats.total_validations ? Math.round((stats.risky_count / stats.total_validations) * 100) : 0,
      icon: AlertTriangle,
      color: 'text-amber-600',
      bg: 'bg-amber-50 dark:bg-amber-950',
      border: 'border-amber-100 dark:border-amber-900',
    },
    {
      label: 'Disposable',
      value: stats.disposable_count,
      icon: Trash2,
      color: 'text-purple-600',
      bg: 'bg-purple-50 dark:bg-purple-950',
      border: 'border-purple-100 dark:border-purple-900',
    },
    {
      label: 'Spam Traps',
      value: stats.spam_trap_count,
      icon: ShieldAlert,
      color: 'text-rose-600',
      bg: 'bg-rose-50 dark:bg-rose-950',
      border: 'border-rose-100 dark:border-rose-900',
    },
    {
      label: 'Avg. Score',
      value: stats.average_score,
      suffix: '/100',
      icon: TrendingUp,
      color: 'text-sky-600',
      bg: 'bg-sky-50 dark:bg-sky-950',
      border: 'border-sky-100 dark:border-sky-900',
    },
    {
      label: 'Bulk Jobs',
      value: stats.total_bulk_jobs,
      icon: HelpCircle,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50 dark:bg-indigo-950',
      border: 'border-indigo-100 dark:border-indigo-900',
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.label} className={cn('border', card.border)}>
            <CardContent className="pt-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                    {card.label}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {typeof card.value === 'number' && !card.suffix
                      ? formatNumber(Math.floor(card.value))
                      : card.value}
                    {card.suffix && <span className="text-sm font-normal text-gray-500 ml-1">{card.suffix}</span>}
                  </p>
                  {card.pct !== undefined && (
                    <p className={cn('text-xs font-medium mt-1', card.color)}>
                      {card.pct}% of total
                    </p>
                  )}
                </div>
                <div className={cn('p-2.5 rounded-xl', card.bg)}>
                  <Icon className={cn('w-5 h-5', card.color)} />
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
