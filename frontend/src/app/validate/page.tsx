'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { ValidationResultCard } from '@/components/validation/result-card'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { validationApi } from '@/lib/api'
import { ValidationResult } from '@/types'
import { useAuthStore } from '@/store/auth'
import toast from 'react-hot-toast'
import { Mail, Search, Zap } from 'lucide-react'

export default function ValidatePage() {
  const [email, setEmail] = useState('')
  const [checkSmtp, setCheckSmtp] = useState(true)
  const [result, setResult] = useState<ValidationResult | null>(null)
  const { refreshSubscription, subscription, setSubscription } = useAuthStore()

  const { mutate: validate, isPending } = useMutation({
    mutationFn: () => validationApi.validateSingle(email, checkSmtp),
    onSuccess: (response) => {
      setResult(response.data.result)
      // Immediately decrement locally for instant feedback, then sync from server
      if (subscription) {
        setSubscription({ ...subscription, available_credits: Math.max(0, subscription.available_credits - 1) })
      }
      refreshSubscription()
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.error?.message || 'Validation failed'
      toast.error(msg)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return
    validate()
  }

  return (
    <AppLayout
      title="Validate Email"
      subtitle="Check a single email address in real-time"
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Input Card */}
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-3">
                <Input
                  placeholder="Enter email address (e.g. john@example.com)"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  leftIcon={<Mail className="w-4 h-4" />}
                  type="email"
                  className="flex-1"
                  autoFocus
                />
                <Button
                  type="submit"
                  loading={isPending}
                  icon={<Search className="w-4 h-4" />}
                  size="md"
                  className="shrink-0"
                >
                  Validate
                </Button>
              </div>

              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={checkSmtp}
                    onChange={(e) => setCheckSmtp(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-amber-500" />
                    SMTP verification (more accurate, slower)
                  </span>
                </label>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Placeholder when no result */}
        {!result && !isPending && (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-violet-100 dark:from-blue-950 dark:to-violet-950 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-10 h-10 text-blue-500 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Enter an email to validate</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm max-w-sm mx-auto">
              We'll check syntax, DNS records, MX records, SMTP verification, disposable email detection, and more.
            </p>

            <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-xl mx-auto">
              {['Syntax Check', 'MX Records', 'SMTP Verify', 'Disposable'].map((label) => (
                <div key={label} className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-xs text-gray-600 dark:text-gray-400 font-medium">
                  ✓ {label}
                </div>
              ))}
            </div>
          </div>
        )}

        {isPending && (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 rounded-full border-4 border-blue-200 dark:border-blue-900" />
              <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-900 dark:text-white">Validating email...</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Running {checkSmtp ? '7' : '5'} validation checks</p>
            </div>
          </div>
        )}

        {result && <ValidationResultCard result={result} />}
      </div>
    </AppLayout>
  )
}
