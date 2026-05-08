'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/auth'
import {
  LayoutDashboard, Mail, Upload, History, Key, CreditCard,
  Webhook, Settings, LogOut, ChevronRight, Zap, Shield
} from 'lucide-react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/validate', label: 'Validate Email', icon: Mail },
  { href: '/bulk', label: 'Bulk Upload', icon: Upload },
  { href: '/history', label: 'History', icon: History },
  { divider: true },
  { href: '/api-keys', label: 'API Keys', icon: Key },
  { href: '/webhooks', label: 'Webhooks', icon: Webhook },
  { divider: true },
  { href: '/billing', label: 'Billing', icon: CreditCard },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, subscription, logout } = useAuthStore()

  return (
    <aside className="flex flex-col w-64 min-h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-center w-9 h-9 bg-gradient-to-br from-blue-600 to-violet-600 rounded-xl">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-gray-900 dark:text-white text-lg">EmailGuard</span>
          <p className="text-xs text-gray-500 dark:text-gray-400">Email Intelligence</p>
        </div>
      </div>

      {/* Credits badge */}
      {subscription && (
        <div className="mx-4 mt-4 px-3 py-2 bg-gradient-to-r from-blue-50 to-violet-50 dark:from-blue-950 dark:to-violet-950 rounded-lg border border-blue-100 dark:border-blue-900">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Credits</span>
            </div>
            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
              {subscription.available_credits.toLocaleString()}
            </span>
          </div>
          <div className="mt-1.5 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-gradient-to-r from-blue-500 to-violet-500 h-1.5 rounded-full transition-all"
              style={{
                width: `${Math.min((subscription.available_credits / (subscription.plan_details?.credits || 100)) * 100, 100)}%`
              }}
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map((item, i) => {
          if ('divider' in item) {
            return <div key={i} className="my-3 border-t border-gray-200 dark:border-gray-800" />
          }

          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group',
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? 'text-white' : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300')} />
              {item.label}
              {isActive && <ChevronRight className="w-3 h-3 ml-auto" />}
            </Link>
          )
        })}
      </nav>

      {/* User profile */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white text-sm font-semibold">
            {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {user?.full_name || user?.email}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate capitalize">
              {subscription?.plan_details?.name || 'Free'} Plan
            </p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
