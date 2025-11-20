import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useProducts } from '@/hooks/useApi'
import ErrorMessage from './ErrorMessage'
import SkeletonLoader from './SkeletonLoader'

interface ProductChartProps {
  limit?: number
}

function ProductChart({ limit = 10 }: ProductChartProps) {
  const { data, loading, error, refetch } = useProducts({
    limit,
    sort: 'total_revenue',
    order: 'desc',
  })

  if (loading) {
    return <SkeletonLoader height="300px" />
  }

  if (error) {
    return (
      <ErrorMessage
        message={error.message || 'Failed to load product data'}
        onRetry={refetch}
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-20 text-gray-600">
        No product data available
      </div>
    )
  }

  // Format data for Recharts
  const chartData = data.map((item) => ({
    name: item.product_name.length > 15
      ? item.product_name.substring(0, 15) + '...'
      : item.product_name,
    fullName: item.product_name,
    revenue: item.total_revenue,
    unitsSold: item.units_sold,
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200 max-w-xs">
          <p className="font-semibold text-gray-900 text-sm mb-1">
            {payload[0].payload.fullName}
          </p>
          <p className="text-sm text-primary-600">
            Revenue: ₪{payload[0].value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">
            Units Sold: {payload[0].payload.unitsSold.toLocaleString()}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="name"
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `₪${value.toLocaleString()}`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: '14px' }}
          iconType="rect"
        />
        <Bar
          dataKey="revenue"
          fill="#0ea5e9"
          name="Revenue (₪)"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default ProductChart
