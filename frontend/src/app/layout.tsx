import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'EmailGuard - Email Validation & Intelligence Platform',
    template: '%s | EmailGuard',
  },
  description: 'Professional email validation, SMTP verification, disposable email detection, and bulk validation platform.',
  keywords: ['email validation', 'email verification', 'SMTP check', 'bulk email validation', 'disposable email'],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
