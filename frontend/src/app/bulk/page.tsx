'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StatusBadge } from '@/components/ui/badge'
import { bulkApi } from '@/lib/api'
import { BulkJob } from '@/types'
import { formatDateTime, formatNumber, formatDuration, cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import { Upload, FileText, Download, X, RefreshCw, Eye, Clock } from 'lucide-react'

export default function BulkPage() {
  const [jobName, setJobName] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedJob, setSelectedJob] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: jobsData, isLoading } = useQuery({
    queryKey: ['bulk-jobs'],
    queryFn: () => bulkApi.getJobs().then((r) => r.data),
    refetchInterval: (data) => {
      const hasActive = data?.results?.some((j: BulkJob) =>
        ['pending', 'processing'].includes(j.status)
      )
      return hasActive ? 3000 : false
    },
  })

  const { mutate: uploadFile, isPending: uploading } = useMutation({
    mutationFn: () => {
      const formData = new FormData()
      formData.append('file', selectedFile!)
      if (jobName) formData.append('name', jobName)
      return bulkApi.uploadFile(formData)
    },
    onSuccess: (response) => {
      toast.success(`Job created! Processing ${response.data.job.total_emails.toLocaleString()} emails.`)
      setSelectedFile(null)
      setJobName('')
      queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.error?.message || 'Upload failed'
      toast.error(msg)
    },
  })

  const { mutate: cancelJob } = useMutation({
    mutationFn: (jobId: string) => bulkApi.cancelJob(jobId),
    onSuccess: () => {
      toast.success('Job cancelled')
      queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'text/plain': ['.txt'] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  })

  const jobs: BulkJob[] = jobsData?.results || []

  return (
    <AppLayout
      title="Bulk Validation"
      subtitle="Upload CSV files to validate thousands of emails"
    >
      <div className="space-y-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Email List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Dropzone */}
              <div
                {...getRootProps()}
                className={cn(
                  'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
                  isDragActive
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                    : selectedFile
                    ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-950/20'
                    : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                )}
              >
                <input {...getInputProps()} />
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="w-8 h-8 text-emerald-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 dark:text-white">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setSelectedFile(null) }}
                      className="ml-2 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full"
                    >
                      <X className="w-4 h-4 text-gray-500" />
                    </button>
                  </div>
                ) : (
                  <>
                    <Upload className={cn('w-10 h-10 mx-auto mb-3', isDragActive ? 'text-blue-500' : 'text-gray-400')} />
                    <p className="text-base font-medium text-gray-700 dark:text-gray-300">
                      {isDragActive ? 'Drop your CSV here' : 'Drag & drop your CSV file'}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      or <span className="text-blue-600 font-medium">browse to upload</span>
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-3">
                      Supports .csv and .txt • Max 50MB • Up to 500,000 emails
                    </p>
                  </>
                )}
              </div>

              {selectedFile && (
                <div className="flex gap-3">
                  <Input
                    placeholder="Job name (optional)"
                    value={jobName}
                    onChange={(e) => setJobName(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    onClick={() => uploadFile()}
                    loading={uploading}
                    icon={<Upload className="w-4 h-4" />}
                  >
                    Start Validation
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Jobs Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Validation Jobs</CardTitle>
              <Button
                variant="outline"
                size="sm"
                icon={<RefreshCw className="w-3.5 h-3.5" />}
                onClick={() => queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })}
              >
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-12">
                <Upload className="w-10 h-10 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No bulk jobs yet. Upload a CSV to get started.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-800">
                      <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">File</th>
                      <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                      <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">Progress</th>
                      <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">Results</th>
                      <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">Created</th>
                      <th className="text-right py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wide">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {jobs.map((job) => (
                      <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                        <td className="py-3 px-2">
                          <p className="font-medium text-sm text-gray-900 dark:text-white truncate max-w-[180px]">
                            {job.name || job.original_filename}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{formatNumber(job.total_emails)} emails</p>
                        </td>
                        <td className="py-3 px-2">
                          <span className={cn(
                            'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium',
                            job.status === 'completed' && 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400',
                            job.status === 'processing' && 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
                            job.status === 'pending' && 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
                            job.status === 'failed' && 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
                            job.status === 'cancelled' && 'bg-gray-100 text-gray-500',
                          )}>
                            {job.status}
                          </span>
                        </td>
                        <td className="py-3 px-2 min-w-[140px]">
                          {['processing', 'completed'].includes(job.status) ? (
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {formatNumber(job.processed_emails)}/{formatNumber(job.total_emails)}
                                </span>
                                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                                  {job.progress_percentage}%
                                </span>
                              </div>
                              <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                                <div
                                  className={cn('h-1.5 rounded-full transition-all', job.status === 'completed' ? 'bg-emerald-500' : 'bg-blue-500')}
                                  style={{ width: `${job.progress_percentage}%` }}
                                />
                              </div>
                            </div>
                          ) : (
                            <span className="text-xs text-gray-400">—</span>
                          )}
                        </td>
                        <td className="py-3 px-2">
                          {job.status === 'completed' ? (
                            <div className="flex gap-2 text-xs">
                              <span className="text-emerald-600 font-medium">{formatNumber(job.valid_count)} valid</span>
                              <span className="text-red-500">{formatNumber(job.invalid_count)} invalid</span>
                            </div>
                          ) : (
                            <span className="text-xs text-gray-400">—</span>
                          )}
                        </td>
                        <td className="py-3 px-2">
                          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {formatDateTime(job.created_at)}
                          </span>
                        </td>
                        <td className="py-3 px-2">
                          <div className="flex items-center justify-end gap-2">
                            {job.status === 'completed' && (
                              <a
                                href={bulkApi.downloadResults(job.id)}
                                download
                                className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 rounded-lg hover:bg-emerald-200 dark:hover:bg-emerald-900 transition-colors"
                              >
                                <Download className="w-3 h-3" /> CSV
                              </a>
                            )}
                            {['pending', 'processing'].includes(job.status) && (
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => cancelJob(job.id)}
                              >
                                Cancel
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
