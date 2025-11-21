import { TrendingUp, Lightbulb, TrendingDown, AlertTriangle } from 'lucide-react';
import { CategoryPieChart } from '@/components/CategoryPieChart';
import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency } from '@/lib/utils/hebrew';
import { useCategories } from '@/hooks/useCBSData';
import { CategoryBreakdown } from '@/lib/types';

const Revenue = () => {
  const { data: categoriesData, isLoading, error } = useCategories();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  if (error || !categoriesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
        </div>
      </div>
    );
  }

  // Transform to chart format
  const chartData: CategoryBreakdown[] = categoriesData.categories
    .slice(0, 7)
    .map(cat => ({
      category: cat.category,
      value: parseFloat(cat.total_revenue),
      percentage: parseFloat(parseFloat(cat.market_share_pct).toFixed(1)),
    }));

  // Get categories included in "Other"
  const otherCategories = categoriesData.categories
    .slice(7)
    .map(cat => cat.category);

  // Calculate total revenue
  const totalRevenue = categoriesData.categories.reduce(
    (sum, cat) => sum + parseFloat(cat.total_revenue),
    0
  );

  // Top 3 categories
  const top3Revenue = categoriesData.categories
    .slice(0, 3)
    .reduce((sum, cat) => sum + parseFloat(cat.total_revenue), 0);

  const top3Percentage = (top3Revenue / totalRevenue) * 100;

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
    error: TrendingDown,
  };

  // Table columns
  const columns = [
    {
      key: 'category' as const,
      label: 'קטגוריה',
      sortable: true
    },
    {
      key: 'transaction_count' as const,
      label: 'מספר עסקאות',
      sortable: true,
      render: (value: number) => value.toLocaleString('he-IL')
    },
    {
      key: 'total_revenue' as const,
      label: 'סך הכנסות',
      sortable: true,
      render: (value: string) => (
        <span className="font-semibold">{formatCurrency(parseFloat(value))}</span>
      )
    },
    {
      key: 'market_share_pct' as const,
      label: 'נתח שוק',
      sortable: true,
      render: (value: string) => `${parseFloat(value).toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ניתוח הכנסות</h1>
        <p className="text-muted-foreground" dir="rtl">
          התפלגות הוצאות לפי קטגוריות הלמ"ס
        </p>
      </div>

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="קטגוריה מובילה"
            description={`${categoriesData.categories[0].category} מובילה בהכנסות`}
            metric={formatCurrency(parseFloat(categoriesData.categories[0].total_revenue))}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="ריכוז שוק"
            description="3 הקטגוריות המובילות מהוות חלק גדול מהשוק"
            metric={`${top3Percentage.toFixed(1)}%`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="גיוון קטגוריות"
            description={`${categoriesData.categories.length} קטגוריות פעילות`}
            metric={categoriesData.categories.length.toString()}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="סך הכנסות"
            description="סך כל ההוצאות בכל הקטגוריות"
            metric={formatCurrency(totalRevenue)}
            type="info"
          />
        </div>
      </div>

      {/* Category Pie Chart */}
      <CategoryPieChart data={chartData} title="פילוח הכנסות לפי קטגוריה" otherCategories={otherCategories} />

      {/* Top Categories Table */}
      <div className="bg-card rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4" dir="rtl">קטגוריות מובילות - Top 5</h3>
        <div className="space-y-3">
          {categoriesData.categories.slice(0, 5).map((category, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm font-medium" dir="rtl">{category.category}</span>
              <div className="flex items-center gap-3">
                <div className="text-end">
                  <p className="text-sm font-semibold" dir="rtl">
                    {formatCurrency(parseFloat(category.total_revenue))}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {parseFloat(category.market_share_pct).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Categories Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות</h2>
        <DataTable data={categoriesData.categories} columns={columns} />
      </div>
    </div>
  );
};

export default Revenue;
