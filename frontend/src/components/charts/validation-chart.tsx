'use client'

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts'
import { ValidationStats } from '@/types'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { formatDate } from '@/lib/utils'

const STATUS_CHART_DATA_COLORS = [
  '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#3b82f6', '#6b7280'
]

interface ValidationChartProps {
  stats: ValidationStats
}

export function ValidationAreaChart({ stats }: ValidationChartProps) {
  const data = stats.daily_breakdown.map((d) => ({
    date: formatDate(d.date),
    count: d.count,
    avg_score: Math.round(d.avg_score || 0),
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Validation Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} className="fill-gray-500" />
            <YAxis tick={{ fontSize: 11 }} className="fill-gray-500" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg, #fff)',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#colorCount)"
              name="Validations"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function StatusDistributionChart({ stats }: { stats: ValidationStats['overview'] }) {
  const data = [
    { name: 'Valid', value: stats.valid_count, color: '#10b981' },
    { name: 'Invalid', value: stats.invalid_count, color: '#ef4444' },
    { name: 'Risky', value: stats.risky_count, color: '#f59e0b' },
    { name: 'Disposable', value: stats.disposable_count, color: '#8b5cf6' },
    { name: 'Catch-All', value: stats.catch_all_count, color: '#3b82f6' },
    { name: 'Spam Trap', value: stats.spam_trap_count, color: '#ec4899' },
    { name: 'Unknown', value: stats.unknown_count, color: '#6b7280' },
  ].filter((d) => d.value > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Status Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={110}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Legend
              iconType="circle"
              iconSize={8}
              formatter={(value) => (
                <span className="text-xs text-gray-600">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
