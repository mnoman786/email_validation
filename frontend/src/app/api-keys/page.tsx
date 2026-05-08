'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiKeysApi } from '@/lib/api'
import { APIKey } from '@/types'
import { formatDateTime, cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import { Key, Plus, Copy, Trash2, Eye, EyeOff, Clock, Zap, AlertTriangle } from 'lucide-react'

export default function APIKeysPage() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyPermissions, setNewKeyPermissions] = useState('validate')
  const [createdKey, setCreatedKey] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeysApi.list().then((r) => r.data),
  })

  const { mutate: createKey, isPending: creating } = useMutation({
    mutationFn: () => apiKeysApi.create({ name: newKeyName, permissions: newKeyPermissions }),
    onSuccess: (response) => {
      setCreatedKey(response.data.api_key.key)
      setNewKeyName('')
      setShowCreateForm(false)
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
    onError: () => toast.error('Failed to create API key'),
  })

  const { mutate: deleteKey } = useMutation({
    mutationFn: (id: string) => apiKeysApi.delete(id),
    onSuccess: () => {
      toast.success('API key deactivated')
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  const keys: APIKey[] = data?.results || data || []

  return (
    <AppLayout title="API Keys" subtitle="Manage API keys for programmatic access">
      <div className="max-w-4xl space-y-6">
        {/* New key reveal */}
        {createdKey && (
          <div className="p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-amber-800 dark:text-amber-200 text-sm">Save your API key now!</p>
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1 mb-3">
                  This key will not be shown again. Copy and store it securely.
                </p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 bg-amber-100 dark:bg-amber-900 px-3 py-2 rounded-lg text-sm font-mono text-amber-900 dark:text-amber-100 break-all">
                    {createdKey}
                  </code>
                  <Button
                    variant="outline"
                    size="sm"
                    icon={<Copy className="w-4 h-4" />}
                    onClick={() => copyToClipboard(createdKey)}
                  >
                    Copy
                  </Button>
                </div>
              </div>
              <button onClick={() => setCreatedKey(null)} className="text-amber-600 hover:text-amber-800">✕</button>
            </div>
          </div>
        )}

        {/* Create Form */}
        {showCreateForm ? (
          <Card>
            <CardHeader>
              <CardTitle>Create New API Key</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  label="Key Name"
                  placeholder="e.g. Production App, Testing"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Permissions</label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {['read', 'validate', 'bulk', 'full'].map((p) => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setNewKeyPermissions(p)}
                        className={cn(
                          'px-3 py-2 rounded-lg text-sm font-medium border transition-colors capitalize',
                          newKeyPermissions === p
                            ? 'bg-blue-600 border-blue-600 text-white'
                            : 'border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-blue-400'
                        )}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex gap-3">
                  <Button
                    onClick={() => createKey()}
                    loading={creating}
                    disabled={!newKeyName.trim()}
                  >
                    Create Key
                  </Button>
                  <Button variant="outline" onClick={() => setShowCreateForm(false)}>Cancel</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {keys.length} of 10 API keys used
            </p>
            <Button
              onClick={() => setShowCreateForm(true)}
              icon={<Plus className="w-4 h-4" />}
              disabled={keys.length >= 10}
            >
              Create API Key
            </Button>
          </div>
        )}

        {/* Keys List */}
        <Card>
          <CardContent className="pt-0">
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
              </div>
            ) : keys.length === 0 ? (
              <div className="text-center py-12">
                <Key className="w-10 h-10 text-gray-300 dark:text-gray-700 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No API keys yet</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {keys.map((key) => (
                  <div key={key.id} className="py-4 first:pt-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                          <Key className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{key.name}</p>
                          <div className="flex items-center gap-3 mt-1">
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                              {key.key_prefix}••••••••
                            </code>
                            <span className={cn(
                              'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium capitalize',
                              'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400'
                            )}>
                              {key.permissions}
                            </span>
                            {!key.is_active && (
                              <span className="text-xs text-red-500 font-medium">Inactive</span>
                            )}
                          </div>
                          <div className="flex items-center gap-4 mt-1.5">
                            <span className="text-xs text-gray-400 flex items-center gap-1">
                              <Zap className="w-3 h-3" /> {key.total_requests.toLocaleString()} requests
                            </span>
                            {key.last_used_at && (
                              <span className="text-xs text-gray-400 flex items-center gap-1">
                                <Clock className="w-3 h-3" /> Last used {formatDateTime(key.last_used_at)}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Button
                          variant="outline"
                          size="sm"
                          icon={<Copy className="w-3.5 h-3.5" />}
                          onClick={() => copyToClipboard(key.key_prefix + '...')}
                        >
                          Copy
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          icon={<Trash2 className="w-3.5 h-3.5" />}
                          onClick={() => {
                            if (confirm('Deactivate this API key?')) deleteKey(key.id)
                          }}
                        >
                          Revoke
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Usage Example */}
        <Card>
          <CardHeader>
            <CardTitle>API Usage Example</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-950 text-gray-100 p-4 rounded-xl text-xs overflow-x-auto">
{`# Validate a single email
curl -X POST https://api.emailguard.io/api/v1/validation/validate/ \\
  -H "X-API-Key: eg_your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"email": "test@example.com", "check_smtp": true}'

# Response
{
  "email": "test@example.com",
  "valid": true,
  "score": 87,
  "status": "valid",
  "is_disposable": false,
  "smtp_check": true,
  "mx_found": true,
  "domain_reputation": "good",
  "risk_level": "low",
  "suggested_action": "safe_to_send"
}`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
