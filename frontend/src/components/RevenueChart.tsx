import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useRevenue } from '@/hooks/useApi'
import ErrorMessage from './ErrorMessage'
import SkeletonLoader from './SkeletonLoader'

interface RevenueChartProps {
  limit?: number
  grouping?: 'day' | 'week' | 'month'
}

function RevenueChart({ limit = 7, grouping = 'day' }: RevenueChartProps) {
  const { data, loading, error, refetch } = useRevenue({ limit, grouping })

  if (loading) {
    return <SkeletonLoader height="300px" />
  }

  if (error) {
    return (
      <ErrorMessage
        message={error.message || 'Failed to load revenue data'}
        onRetry={refetch}
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-20 text-gray-600">
        No revenue data available
      </div>
    )
  }

  // Format data for Recharts
  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString('he-IL', {
      month: 'short',
      day: 'numeric',
    }),
    revenue: item.revenue,
    transactions: item.transactions || 0,
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{payload[0].payload.date}</p>
          <p className="text-sm text-primary-600">
            Revenue: ₪{payload[0].value.toLocaleString()}
          </p>
          {payload[1] && (
            <p className="text-sm text-gray-600">
              Transactions: {payload[1].value}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="date"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `₪${value.toLocaleString()}`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '14px' }}
          iconType="line"
        />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="#0ea5e9"
          strokeWidth={2}
          dot={{ fill: '#0ea5e9', r: 4 }}
          activeDot={{ r: 6 }}
          name="Revenue (₪)"
        />
        {chartData[0]?.transactions !== undefined && (
          <Line
            type="monotone"
            dataKey="transactions"
            stroke="#64748b"
            strokeWidth={2}
            dot={{ fill: '#64748b', r: 4 }}
            activeDot={{ r: 6 }}
            name="Transactions"
            yAxisId={1}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}

export default RevenueChart
