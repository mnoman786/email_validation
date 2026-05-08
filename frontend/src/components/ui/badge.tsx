import { cn } from '@/lib/utils'
import { ValidationStatus } from '@/types'
import { STATUS_COLORS, STATUS_LABELS } from '@/lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'outline'
  className?: string
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variant === 'outline' ? 'border-current bg-transparent' : '',
        className
      )}
    >
      {children}
    </span>
  )
}

interface StatusBadgeProps {
  status: ValidationStatus
  size?: 'sm' | 'md'
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium border',
        STATUS_COLORS[status],
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs'
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
