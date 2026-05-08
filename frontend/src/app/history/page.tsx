'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/badge'
import { validationApi } from '@/lib/api'
import { ValidationResult, ValidationStatus } from '@/types'
import { formatDateTime, getScoreColor, cn } from '@/lib/utils'
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'

const STATUS_FILTERS: { label: string; value: string }[] = [
  { label: 'All', value: '' },
  { label: 'Valid', value: 'valid' },
  { label: 'Invalid', value: 'invalid' },
  { label: 'Risky', value: 'risky' },
  { label: 'Disposable', value: 'disposable' },
  { label: 'Catch-All', value: 'catch_all' },
  { label: 'Spam Trap', value: 'spam_trap' },
  { label: 'Unknown', value: 'unknown' },
]

export default function HistoryPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['validation-history', page, search, statusFilter],
    queryFn: () => validationApi.getHistory({
      page,
      search,
      ...(statusFilter && { status: statusFilter }),
    }).then((r) => r.data),
  })

  const results: ValidationResult[] = data?.results || []
  const pagination = data?.pagination

  return (
    <AppLayout title="Validation History" subtitle="Browse and filter your past validation results">
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4">
            <Input
              placeholder="Search by email or domain..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              leftIcon={<Search className="w-4 h-4" />}
              className="flex-1"
            />
            <div className="flex items-center gap-1 overflow-x-auto">
              {STATUS_FILTERS.map((f) => (
                <button
                  key={f.value}
                  onClick={() => { setStatusFilter(f.value); setPage(1) }}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors',
                    statusFilter === f.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                  )}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No results found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-800">
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase">Score</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Domain</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">MX</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">SMTP</th>
                      <th className="text-left py-3 px-3 text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {results.map((result) => (
                      <tr key={result.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30">
                        <td className="py-3 px-3 font-medium text-gray-900 dark:text-white max-w-[200px] truncate">
                          {result.email}
                        </td>
                        <td className="py-3 px-3">
                          <StatusBadge status={result.status} size="sm" />
                        </td>
                        <td className="py-3 px-3">
                          <span className={cn('font-bold text-base', getScoreColor(result.score))}>
                            {result.score}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-gray-500 dark:text-gray-400 hidden md:table-cell">
                          {result.domain}
                        </td>
                        <td className="py-3 px-3 hidden lg:table-cell">
                          <span className={result.mx_found ? 'text-emerald-600' : 'text-red-500'}>
                            {result.mx_found ? '✓' : '✗'}
                          </span>
                        </td>
                        <td className="py-3 px-3 hidden lg:table-cell">
                          <span className={result.smtp_check ? 'text-emerald-600' : 'text-gray-400'}>
                            {result.smtp_check ? '✓' : '—'}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                          {formatDateTime(result.validated_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {pagination && pagination.total_pages > 1 && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Showing {((page - 1) * pagination.page_size) + 1}–{Math.min(page * pagination.page_size, pagination.count)} of {pagination.count}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      icon={<ChevronLeft className="w-4 h-4" />}
                      disabled={page === 1}
                      onClick={() => setPage(p => p - 1)}
                    >
                      Prev
                    </Button>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {page} / {pagination.total_pages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === pagination.total_pages}
                      onClick={() => setPage(p => p + 1)}
                    >
                      Next <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </AppLayout>
  )
}
