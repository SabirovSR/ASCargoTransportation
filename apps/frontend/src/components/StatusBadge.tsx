import clsx from 'clsx'
import { RouteStatus } from '../api/types'

interface StatusBadgeProps {
  status: RouteStatus
}

const statusConfig: Record<RouteStatus, { label: string; className: string }> = {
  draft: { label: 'Draft', className: 'badge-draft' },
  active: { label: 'Active', className: 'badge-active' },
  completed: { label: 'Completed', className: 'badge-completed' },
  cancelled: { label: 'Cancelled', className: 'badge-cancelled' },
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <span className={clsx('badge', config.className)}>
      {config.label}
    </span>
  )
}
