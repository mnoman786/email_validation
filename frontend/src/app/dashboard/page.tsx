'use client'

import { useQuery } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { ValidationAreaChart, StatusDistributionChart } from '@/components/charts/validation-chart'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/badge'
import { validationApi, bulkApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import Link from 'next/link'
import { Mail, Upload, ArrowRight, Clock } from 'lucide-react'

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['validation-stats', 30],
    queryFn: () => validationApi.getStats(30).then((r) => r.data),
  })

  const { data: recentHistory } = useQuery({
    queryKey: ['validation-history', 'recent'],
    queryFn: () => validationApi.getHistory({ page_size: 5 }).then((r) => r.data),
  })

  const { data: recentJobs } = useQuery({
    queryKey: ['bulk-jobs', 'recent'],
    queryFn: () => bulkApi.getJobs({ page_size: 5 }).then((r) => r.data),
  })

  if (statsLoading) {
    return (
      <AppLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout
      title="Dashboard"
      subtitle="Your email validation overview"
    >
      <div className="space-y-6">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link href="/validate">
            <div className="flex items-center gap-4 p-5 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl text-white hover:from-blue-700 hover:to-blue-800 transition-all group cursor-pointer shadow-lg shadow-blue-600/20">
              <div className="p-3 bg-white/20 rounded-xl">
                <Mail className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <p className="font-semibold">Validate Email</p>
                <p className="text-sm text-blue-200">Single email verification</p>
              </div>
              <ArrowRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </Link>

          <Link href="/bulk">
            <div className="flex items-center gap-4 p-5 bg-gradient-to-br from-violet-600 to-violet-700 rounded-xl text-white hover:from-violet-700 hover:to-violet-800 transition-all group cursor-pointer shadow-lg shadow-violet-600/20">
              <div className="p-3 bg-white/20 rounded-xl">
                <Upload className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <p className="font-semibold">Bulk Upload</p>
                <p className="text-sm text-violet-200">Validate thousands at once</p>
              </div>
              <ArrowRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </Link>
        </div>

        {/* Stats */}
        {stats && <StatsCards stats={stats.overview} />}

        {/* Charts */}
        {stats && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ValidationAreaChart stats={stats} />
            </div>
            <StatusDistributionChart stats={stats.overview} />
          </div>
        )}

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Validations */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Validations</CardTitle>
                <Link href="/history">
                  <Button variant="ghost" size="sm">View all <ArrowRight className="w-3.5 h-3.5" /></Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentHistory?.results?.length > 0 ? (
                  recentHistory.results.map((result: any) => (
                    <div key={result.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{result.email}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-0.5">
                          <Clock className="w-3 h-3" /> {formatDateTime(result.validated_at)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 ml-3">
                        <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{result.score}</span>
                        <StatusBadge status={result.status} size="sm" />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Mail className="w-8 h-8 text-gray-300 dark:text-gray-700 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">No validations yet</p>
                    <Link href="/validate">
                      <Button size="sm" className="mt-3">Validate an email</Button>
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Bulk Jobs */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Bulk Jobs</CardTitle>
                <Link href="/bulk">
                  <Button variant="ghost" size="sm">View all <ArrowRight className="w-3.5 h-3.5" /></Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentJobs?.results?.length > 0 ? (
                  recentJobs.results.map((job: any) => (
                    <div key={job.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{job.name || job.original_filename}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {job.total_emails.toLocaleString()} emails
                        </p>
                        {job.status === 'processing' && (
                          <div className="mt-1.5 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 w-32">
                            <div
                              className="bg-blue-500 h-1.5 rounded-full transition-all"
                              style={{ width: `${job.progress_percentage}%` }}
                            />
                          </div>
                        )}
                      </div>
                      <div className="ml-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          job.status === 'completed' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400' :
                          job.status === 'processing' ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400' :
                          job.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400' :
                          'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
                        }`}>
                          {job.status}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Upload className="w-8 h-8 text-gray-300 dark:text-gray-700 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">No bulk jobs yet</p>
                    <Link href="/bulk">
                      <Button size="sm" className="mt-3">Upload CSV</Button>
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
