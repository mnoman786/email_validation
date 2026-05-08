'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import toast from 'react-hot-toast'
import { User, Lock, Bell, Shield } from 'lucide-react'

export default function SettingsPage() {
  const { user, setUser } = useAuthStore()
  const [profile, setProfile] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    company: user?.company || '',
    timezone: user?.timezone || 'UTC',
  })
  const [passwords, setPasswords] = useState({ old_password: '', new_password: '' })

  const { mutate: updateProfile, isPending: updatingProfile } = useMutation({
    mutationFn: () => authApi.updateMe(profile),
    onSuccess: (response) => {
      setUser(response.data.user || response.data)
      toast.success('Profile updated')
    },
    onError: () => toast.error('Failed to update profile'),
  })

  const { mutate: changePassword, isPending: changingPassword } = useMutation({
    mutationFn: () => authApi.changePassword(passwords),
    onSuccess: () => {
      toast.success('Password changed successfully')
      setPasswords({ old_password: '', new_password: '' })
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.error?.details?.old_password?.[0] || 'Failed to change password'
      toast.error(msg)
    },
  })

  return (
    <AppLayout title="Settings" subtitle="Manage your account preferences">
      <div className="max-w-2xl space-y-6">
        {/* Profile */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-500" />
              <CardTitle>Profile Information</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4 pb-4 border-b border-gray-200 dark:border-gray-800">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white text-2xl font-bold">
                {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">{user?.full_name || user?.email}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
                {user?.is_verified ? (
                  <span className="text-xs text-emerald-600 flex items-center gap-1 mt-0.5">
                    <Shield className="w-3 h-3" /> Email verified
                  </span>
                ) : (
                  <span className="text-xs text-amber-600">Email not verified</span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input label="First Name" value={profile.first_name} onChange={e => setProfile({ ...profile, first_name: e.target.value })} />
              <Input label="Last Name" value={profile.last_name} onChange={e => setProfile({ ...profile, last_name: e.target.value })} />
            </div>
            <Input label="Company" value={profile.company} onChange={e => setProfile({ ...profile, company: e.target.value })} />
            <Input label="Email" value={user?.email || ''} disabled helperText="Email cannot be changed" />

            <Button onClick={() => updateProfile()} loading={updatingProfile}>Save Changes</Button>
          </CardContent>
        </Card>

        {/* Password */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-gray-500" />
              <CardTitle>Change Password</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              value={passwords.old_password}
              onChange={e => setPasswords({ ...passwords, old_password: e.target.value })}
            />
            <Input
              label="New Password"
              type="password"
              value={passwords.new_password}
              onChange={e => setPasswords({ ...passwords, new_password: e.target.value })}
              helperText="Minimum 8 characters"
            />
            <Button
              onClick={() => changePassword()}
              loading={changingPassword}
              disabled={!passwords.old_password || !passwords.new_password}
            >
              Change Password
            </Button>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-red-200 dark:border-red-900">
          <CardHeader>
            <CardTitle className="text-red-600 dark:text-red-400">Danger Zone</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <Button variant="danger" onClick={() => toast.error('Contact support to delete your account')}>
              Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
