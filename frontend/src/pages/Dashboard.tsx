import { useDashboard } from '@/hooks/useApi'
import MetricsCard from '@/components/MetricsCard'
import ErrorMessage from '@/components/ErrorMessage'
import SkeletonLoader from '@/components/SkeletonLoader'
import RevenueChart from '@/components/RevenueChart'
import ProductChart from '@/components/ProductChart'
import SankeyDiagram from '@/visualizations/SankeyDiagram'
import { mockCustomerJourneyData } from '@/utils/mockData'

function Dashboard() {
  const { data: metrics, loading, error, refetch } = useDashboard()

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-2">
            Overview of your e-commerce analytics
          </p>
        </div>
        <button
          onClick={refetch}
          disabled={loading}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {error && (
        <ErrorMessage
          message={error.message || 'Failed to load dashboard metrics'}
          onRetry={refetch}
          className="mb-6"
        />
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricsCard
          title="Total Revenue"
          value={metrics ? `₪${metrics.total_revenue.toLocaleString()}` : '₪0'}
          subtitle="All time"
          loading={loading}
          icon={
            <svg
              className="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
        />

        <MetricsCard
          title="Total Customers"
          value={metrics?.total_customers.toLocaleString() || '0'}
          subtitle="Active customers"
          loading={loading}
          icon={
            <svg
              className="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          }
        />

        <MetricsCard
          title="Total Products"
          value={metrics?.total_products.toLocaleString() || '0'}
          subtitle="In catalog"
          loading={loading}
          icon={
            <svg
              className="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          }
        />

        <MetricsCard
          title="Avg Order Value"
          value={metrics ? `₪${metrics.avg_order_value.toFixed(2)}` : '₪0'}
          subtitle="Per transaction"
          loading={loading}
          icon={
            <svg
              className="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          }
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Revenue Trend (Last 7 Days)
          </h3>
          <RevenueChart limit={7} grouping="day" />
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Top 10 Products by Revenue
          </h3>
          <ProductChart limit={10} />
        </div>
      </div>

      {/* Customer Journey Section */}
      <div className="card">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Customer Journey Flow
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Flow from traffic source → product category → outcome
          </p>
        </div>
        {loading ? (
          <SkeletonLoader height="400px" />
        ) : (
          <SankeyDiagram data={mockCustomerJourneyData} width={1000} height={500} />
        )}
      </div>
    </div>
  )
}

export default Dashboard
