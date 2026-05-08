'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/store/auth'
import { authApi } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import toast from 'react-hot-toast'
import { Shield, Mail, Lock, User, Building2, Check } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company: '',
    password: '',
    password_confirm: '',
  })

  const { mutate: register, isPending } = useMutation({
    mutationFn: () => authApi.register(form),
    onSuccess: (response) => {
      const { user, subscription, tokens } = response.data
      setAuth(user, subscription, tokens)
      toast.success('Account created! Welcome to EmailGuard.')
      router.push('/dashboard')
    },
    onError: (error: any) => {
      const details = error?.response?.data?.error?.details
      const msg = details?.email?.[0] || details?.password?.[0] || error?.response?.data?.error?.message || 'Registration failed'
      toast.error(msg)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (form.password !== form.password_confirm) {
      toast.error('Passwords do not match')
      return
    }
    register()
  }

  const features = ['100 free verifications', 'SMTP verification', 'Bulk CSV upload', 'API access']

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left - Branding */}
        <div className="hidden md:block">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-violet-600 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">EmailGuard</span>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">
            The most accurate email validation platform
          </h2>
          <p className="text-slate-400 mb-8">
            Verify millions of emails with real-time SMTP checks, disposable email detection, spam trap identification, and more.
          </p>
          <ul className="space-y-3">
            {features.map((f) => (
              <li key={f} className="flex items-center gap-3 text-slate-300">
                <div className="w-5 h-5 bg-emerald-500/20 border border-emerald-500/30 rounded-full flex items-center justify-center">
                  <Check className="w-3 h-3 text-emerald-400" />
                </div>
                {f}
              </li>
            ))}
          </ul>
        </div>

        {/* Right - Form */}
        <div>
          <div className="md:hidden text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-violet-600 rounded-xl mb-3">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">EmailGuard</h1>
          </div>

          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2">Create your account</h2>
            <p className="text-slate-400 text-sm mb-6">Start with 100 free verifications</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  placeholder="First name"
                  value={form.first_name}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                  leftIcon={<User className="w-4 h-4" />}
                  className="bg-white/10 border-white/20 text-white placeholder-slate-400"
                />
                <Input
                  placeholder="Last name"
                  value={form.last_name}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                  className="bg-white/10 border-white/20 text-white placeholder-slate-400"
                />
              </div>

              <Input
                type="email"
                placeholder="Work email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                leftIcon={<Mail className="w-4 h-4" />}
                required
                className="bg-white/10 border-white/20 text-white placeholder-slate-400"
              />

              <Input
                placeholder="Company (optional)"
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                leftIcon={<Building2 className="w-4 h-4" />}
                className="bg-white/10 border-white/20 text-white placeholder-slate-400"
              />

              <Input
                type="password"
                placeholder="Password (min 8 characters)"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                leftIcon={<Lock className="w-4 h-4" />}
                required
                className="bg-white/10 border-white/20 text-white placeholder-slate-400"
              />

              <Input
                type="password"
                placeholder="Confirm password"
                value={form.password_confirm}
                onChange={(e) => setForm({ ...form, password_confirm: e.target.value })}
                leftIcon={<Lock className="w-4 h-4" />}
                required
                className="bg-white/10 border-white/20 text-white placeholder-slate-400"
              />

              <Button
                type="submit"
                loading={isPending}
                className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 border-0 shadow-lg shadow-blue-600/30"
              >
                Create Account
              </Button>
            </form>

            <p className="text-center text-slate-400 text-xs mt-6">
              By creating an account, you agree to our{' '}
              <a href="#" className="text-blue-400 hover:underline">Terms</a> and{' '}
              <a href="#" className="text-blue-400 hover:underline">Privacy Policy</a>
            </p>

            <p className="text-center text-slate-400 text-sm mt-4">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
