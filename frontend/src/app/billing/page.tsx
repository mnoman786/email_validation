'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { billingApi } from '@/lib/api'
import { CreditPack, Plan, Payment } from '@/types'
import { useAuthStore } from '@/store/auth'
import { formatDateTime, cn } from '@/lib/utils'
import toast from 'react-hot-toast'
import { Zap, Check, CreditCard, History, Star } from 'lucide-react'

export default function BillingPage() {
  const { subscription } = useAuthStore()

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => billingApi.getPlans().then((r) => r.data.plans),
  })

  const { data: creditPacks } = useQuery({
    queryKey: ['credit-packs'],
    queryFn: () => billingApi.getCreditPacks().then((r) => r.data.results),
  })

  const { data: payments } = useQuery({
    queryKey: ['payments'],
    queryFn: () => billingApi.getPayments().then((r) => r.data.results),
  })

  const { mutate: checkout, isPending } = useMutation({
    mutationFn: (packId: string) => billingApi.createCheckout(packId),
    onSuccess: (response) => {
      window.location.href = response.data.checkout_url
    },
    onError: () => toast.error('Failed to start checkout'),
  })

  return (
    <AppLayout title="Billing & Credits" subtitle="Manage your subscription and credits">
      <div className="space-y-8">
        {/* Current Plan */}
        {subscription && (
          <Card className="border-2 border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50 to-violet-50 dark:from-blue-950 dark:to-violet-950">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row sm:items-center gap-6">
                <div className="flex-1">
                  <p className="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide mb-1">Current Plan</p>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
                    {subscription.plan_details?.name || subscription.plan} Plan
                  </h2>
                  <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                    Status: <span className="font-medium capitalize text-emerald-600">{subscription.status}</span>
                  </p>
                </div>
                <div className="text-center">
                  <div className="flex items-center gap-2 justify-center">
                    <Zap className="w-6 h-6 text-amber-500" />
                    <span className="text-3xl font-bold text-gray-900 dark:text-white">
                      {subscription.available_credits.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">credits remaining</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500 dark:text-gray-400">Used</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">
                    {subscription.total_credits_used.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400">all time</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Credit Packs */}
        {creditPacks && creditPacks.length > 0 && (
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Buy Credits</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {(creditPacks as CreditPack[]).map((pack) => (
                <Card key={pack.id} className={cn('relative', pack.is_popular && 'border-2 border-blue-500')}>
                  {pack.is_popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded-full">
                        <Star className="w-3 h-3" /> Popular
                      </span>
                    </div>
                  )}
                  <CardContent className="pt-6 text-center">
                    <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                      ${pack.price_usd}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                      {pack.credits.toLocaleString()} credits
                    </div>
                    <div className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mb-4">
                      ${(pack.price_usd / pack.credits * 1000).toFixed(2)} per 1K verifications
                    </div>
                    <Button
                      onClick={() => checkout(pack.id)}
                      loading={isPending}
                      className="w-full"
                      variant={pack.is_popular ? 'primary' : 'outline'}
                    >
                      Buy Now
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Plans */}
        {plans && (
          <div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Subscription Plans</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {(plans as Plan[]).filter(p => p.id !== 'payg').map((plan) => (
                <Card key={plan.id} className={cn(
                  'relative',
                  subscription?.plan === plan.id && 'border-2 border-emerald-500'
                )}>
                  {subscription?.plan === plan.id && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="px-3 py-1 bg-emerald-600 text-white text-xs font-medium rounded-full">
                        Current Plan
                      </span>
                    </div>
                  )}
                  <CardContent className="pt-6">
                    <p className="font-semibold text-gray-900 dark:text-white">{plan.name}</p>
                    <div className="my-3">
                      {plan.price === 0 ? (
                        <span className="text-2xl font-bold text-gray-900 dark:text-white">Free</span>
                      ) : (
                        <>
                          <span className="text-2xl font-bold text-gray-900 dark:text-white">${plan.price}</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">/mo</span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                      {plan.credits.toLocaleString()} verifications/mo
                    </p>
                    <ul className="space-y-1.5 mb-4">
                      {plan.features.slice(0, 3).map((f) => (
                        <li key={f} className="flex items-start gap-1.5 text-xs text-gray-600 dark:text-gray-400">
                          <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                          {f}
                        </li>
                      ))}
                    </ul>
                    <Button
                      variant={subscription?.plan === plan.id ? 'secondary' : 'outline'}
                      size="sm"
                      className="w-full"
                      disabled={subscription?.plan === plan.id}
                    >
                      {subscription?.plan === plan.id ? 'Current' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Payment History */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-gray-500" />
              <CardTitle>Payment History</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {!payments || payments.length === 0 ? (
              <div className="text-center py-8">
                <CreditCard className="w-8 h-8 text-gray-300 dark:text-gray-700 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">No payments yet</p>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800">
                    <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Credits</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {(payments as Payment[]).map((payment) => (
                    <tr key={payment.id}>
                      <td className="py-3 px-3 text-gray-700 dark:text-gray-300">{payment.description}</td>
                      <td className="py-3 px-3 font-medium">${payment.amount_usd}</td>
                      <td className="py-3 px-3 text-emerald-600">+{payment.credits_added.toLocaleString()}</td>
                      <td className="py-3 px-3">
                        <span className={cn(
                          'px-2 py-0.5 rounded-full text-xs font-medium',
                          payment.status === 'succeeded' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400' :
                          payment.status === 'failed' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-600'
                        )}>
                          {payment.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-xs text-gray-500">{formatDateTime(payment.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
