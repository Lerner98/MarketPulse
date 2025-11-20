import SkeletonLoader from './SkeletonLoader'

interface MetricsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
  loading?: boolean
  trend?: {
    value: number
    label: string
    isPositive: boolean
  }
}

function MetricsCard({ title, value, subtitle, icon, loading, trend }: MetricsCardProps) {
  if (loading) {
    return (
      <div className="card">
        <SkeletonLoader variant="text" height="20px" className="mb-2" />
        <SkeletonLoader variant="text" height="36px" width="60%" className="mb-2" />
        {subtitle && <SkeletonLoader variant="text" height="16px" width="40%" />}
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={`text-sm font-medium ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-sm text-gray-500">{trend.label}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0 p-3 bg-primary-50 rounded-lg">
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

export default MetricsCard
