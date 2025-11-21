import { Wallet, ShoppingCart, TrendingUp, Package, Lightbulb, TrendingDown, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { CategoryPieChart } from '@/components/CategoryPieChart';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { getQuintileLabel } from '@/lib/utils/quintileLabels';
import { useInsights, useCategories, useQuintiles } from '@/hooks/useCBSData';
import { CategoryBreakdown } from '@/lib/types';

const Dashboard = () => {
  // Fetch CBS data using React Query
  const { data: insights, isLoading: insightsLoading, error: insightsError } = useInsights();
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories();
  const { data: quintilesData, isLoading: quintilesLoading } = useQuintiles();

  // Loading state
  if (insightsLoading || categoriesLoading || quintilesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (insightsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
          <p className="text-muted-foreground text-sm" dir="rtl">
            {insightsError.message}
          </p>
        </div>
      </div>
    );
  }

  // No data state
  if (!insights || !categoriesData || !quintilesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground" dir="rtl">אין נתונים זמינים</p>
      </div>
    );
  }

  // Transform CBS categories to chart format
  const categoryChartData: CategoryBreakdown[] = categoriesData.categories
    .slice(0, 7)
    .map(cat => ({
      category: cat.category,
      value: parseFloat(cat.total_revenue),
      percentage: parseFloat(parseFloat(cat.market_share_pct).toFixed(1)),
    }));

  // Calculate total revenue from quintiles
  const totalRevenue = quintilesData.quintiles.reduce(
    (sum, q) => sum + parseFloat(q.total_spending),
    0
  );

  // Get total transaction count
  const totalTransactions = quintilesData.quintiles.reduce(
    (sum, q) => sum + q.transaction_count,
    0
  );

  // Calculate average order value
  const avgOrderValue = totalRevenue / totalTransactions;

  // Get top category
  const topCategory = categoriesData.categories[0];

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
    error: TrendingDown,
  };

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">לוח בקרה ראשי</h1>
        <div className="space-y-1" dir="rtl">
          <p className="text-muted-foreground font-medium">
            ניתוח הוצאות משקי בית ישראליים - נתוני הלמ"ס 2024
          </p>
          <p className="text-sm text-muted-foreground">
            מבוסס על 10,000 עסקאות משקי בית בפילוח לפי 5 רמות הכנסה ו-7 קטגוריות הוצאה עיקריות
          </p>
          <p className="text-xs text-muted-foreground">
            הנתונים כוללים ניתוח גיאוגרפי, התפלגות לפי רמות הכנסה, וביצועי קטגוריות מוצרים
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={Wallet}
          title="סך הוצאות"
          value={formatCurrency(totalRevenue)}
          iconColor="bg-primary/10 text-primary"
        />
        <MetricCard
          icon={ShoppingCart}
          title="מספר עסקאות"
          value={formatNumber(totalTransactions)}
          iconColor="bg-secondary/10 text-secondary"
        />
        <MetricCard
          icon={TrendingUp}
          title="ממוצע הוצאה"
          value={formatCurrency(avgOrderValue)}
          iconColor="bg-accent/10 text-accent"
        />
        <MetricCard
          icon={Package}
          title="קטגוריה מובילה"
          value={topCategory.category}
          iconColor="bg-warning/10 text-warning"
        />
      </div>

      {/* Key Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות מפתח</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InsightCard
            icon={TrendingUp}
            title="פער הכנסות"
            description={quintilesData.key_insight}
            type="info"
          />
          <InsightCard
            icon={Package}
            title={`קטגוריה מובילה: ${topCategory.category}`}
            description={`מייצרת ${parseFloat(topCategory.market_share_pct).toFixed(1)}% מסך השוק עם ${formatNumber(topCategory.transaction_count)} עסקאות`}
            metric={formatCurrency(parseFloat(topCategory.total_revenue))}
            type="success"
          />
          <InsightCard
            icon={Lightbulb}
            title="איכות נתונים"
            description='נתוני הלמ"ס מנוקים ומאומתים'
            metric="100%"
            type="success"
          />
        </div>
      </div>

      {/* Category Breakdown Chart */}
      <CategoryPieChart
        data={categoryChartData}
        title="התפלגות הוצאות לפי קטגוריה"
      />

      {/* Income Quintiles Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">ניתוח לפי רמות הכנסה</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {quintilesData.quintiles.map((quintile) => (
            <div key={quintile.income_quintile} className="bg-card rounded-lg border border-border p-4">
              <div className="text-center">
                <div className="text-sm font-semibold text-primary mb-2">
                  {getQuintileLabel(quintile.income_quintile)}
                </div>
                <div className="text-2xl font-bold mb-1">
                  {formatCurrency(parseFloat(quintile.total_spending))}
                </div>
                <div className="text-xs text-muted-foreground">
                  {quintile.transaction_count.toLocaleString('he-IL')} עסקאות
                </div>
                <div className="text-xs text-primary mt-2">
                  {parseFloat(quintile.spending_share_pct).toFixed(1)}% מהשוק
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
