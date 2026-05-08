'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { webhooksApi } from '@/lib/api'
import { Webhook } from '@/types'
import { formatDateTime, cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import { Webhook as WebhookIcon, Plus, Trash2, Play, CheckCircle2, XCircle, Clock } from 'lucide-react'

const EVENT_OPTIONS = [
  { value: 'bulk_job.completed', label: 'Bulk Job Completed' },
  { value: 'bulk_job.failed', label: 'Bulk Job Failed' },
  { value: 'validation.completed', label: 'Validation Completed' },
  { value: 'credits.low', label: 'Credits Low' },
  { value: 'subscription.cancelled', label: 'Subscription Cancelled' },
]

export default function WebhooksPage() {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', url: '', events: [] as string[] })
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['webhooks'],
    queryFn: () => webhooksApi.list().then((r) => r.data),
  })

  const { mutate: createWebhook, isPending: creating } = useMutation({
    mutationFn: () => webhooksApi.create(form),
    onSuccess: (response) => {
      toast.success('Webhook created!')
      if (response.data.secret) {
        toast(`Secret: ${response.data.secret}\nSave this—it won't be shown again.`, { duration: 10000 })
      }
      setShowForm(false)
      setForm({ name: '', url: '', events: [] })
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
    },
    onError: () => toast.error('Failed to create webhook'),
  })

  const { mutate: deleteWebhook } = useMutation({
    mutationFn: (id: string) => webhooksApi.delete(id),
    onSuccess: () => { toast.success('Webhook deleted'); queryClient.invalidateQueries({ queryKey: ['webhooks'] }) },
  })

  const { mutate: testWebhook } = useMutation({
    mutationFn: (id: string) => webhooksApi.test(id),
    onSuccess: () => toast.success('Test webhook sent!'),
  })

  const toggleEvent = (event: string) => {
    setForm(prev => ({
      ...prev,
      events: prev.events.includes(event)
        ? prev.events.filter(e => e !== event)
        : [...prev.events, event],
    }))
  }

  const webhooks: Webhook[] = data?.results || data || []

  return (
    <AppLayout title="Webhooks" subtitle="Get notified when events occur in your account">
      <div className="max-w-4xl space-y-6">
        {showForm ? (
          <Card>
            <CardHeader>
              <CardTitle>Create Webhook</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Name" placeholder="My Webhook" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
              <Input label="URL" type="url" placeholder="https://yourapp.com/webhooks" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} />
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Events</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {EVENT_OPTIONS.map(opt => (
                    <label key={opt.value} className={cn(
                      'flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors',
                      form.events.includes(opt.value)
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    )}>
                      <input type="checkbox" checked={form.events.includes(opt.value)} onChange={() => toggleEvent(opt.value)} className="sr-only" />
                      <div className={cn('w-4 h-4 rounded border flex items-center justify-center', form.events.includes(opt.value) ? 'bg-blue-600 border-blue-600' : 'border-gray-300')}>
                        {form.events.includes(opt.value) && <CheckCircle2 className="w-3 h-3 text-white" />}
                      </div>
                      <span className="text-sm text-gray-700 dark:text-gray-300">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <Button onClick={() => createWebhook()} loading={creating} disabled={!form.name || !form.url || form.events.length === 0}>Create</Button>
                <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="flex justify-end">
            <Button onClick={() => setShowForm(true)} icon={<Plus className="w-4 h-4" />}>Add Webhook</Button>
          </div>
        )}

        <Card>
          <CardContent className="pt-0">
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
              </div>
            ) : webhooks.length === 0 ? (
              <div className="text-center py-12">
                <WebhookIcon className="w-10 h-10 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No webhooks configured</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {webhooks.map(webhook => (
                  <div key={webhook.id} className="py-5 first:pt-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className={cn('mt-0.5 w-2 h-2 rounded-full', webhook.is_active ? 'bg-emerald-500' : 'bg-gray-400')} />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{webhook.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 font-mono mt-0.5 truncate max-w-[300px]">{webhook.url}</p>
                          <div className="flex flex-wrap gap-1.5 mt-2">
                            {webhook.events.map(e => (
                              <span key={e} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-400">
                                {e}
                              </span>
                            ))}
                          </div>
                          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                            <span className="text-emerald-600">{webhook.total_deliveries} delivered</span>
                            {webhook.failed_deliveries > 0 && <span className="text-red-500">{webhook.failed_deliveries} failed</span>}
                            {webhook.last_triggered_at && <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Last: {formatDateTime(webhook.last_triggered_at)}</span>}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Button variant="outline" size="sm" icon={<Play className="w-3 h-3" />} onClick={() => testWebhook(webhook.id)}>Test</Button>
                        <Button variant="danger" size="sm" icon={<Trash2 className="w-3.5 h-3.5" />} onClick={() => { if (confirm('Delete webhook?')) deleteWebhook(webhook.id) }}>Delete</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
