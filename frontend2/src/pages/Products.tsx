import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { BusinessInsight } from '@/components/BusinessInsight';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { TrendingUp, Lightbulb, AlertTriangle, Package } from 'lucide-react';
import { useCategories } from '@/hooks/useCBSData';

const Products = () => {
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

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  // Calculate total revenue
  const totalRevenue = categoriesData.categories.reduce(
    (sum, cat) => sum + parseFloat(cat.total_revenue),
    0
  );

  // Top category
  const topCategory = categoriesData.categories[0];

  const columns = [
    {
      key: 'category' as const,
      label: 'קטגוריה',
      sortable: true
    },
    {
      key: 'unique_products' as const,
      label: 'מוצרים',
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    {
      key: 'transaction_count' as const,
      label: 'עסקאות',
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    {
      key: 'total_revenue' as const,
      label: 'הכנסות',
      sortable: true,
      render: (value: string) => (
        <span className="font-semibold">{formatCurrency(parseFloat(value))}</span>
      )
    },
    {
      key: 'avg_transaction' as const,
      label: 'ממוצע עסקה',
      sortable: true,
      render: (value: string) => formatCurrency(parseFloat(value))
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ביצועי מוצרים</h1>
        <p className="text-muted-foreground" dir="rtl">
          ניתוח קטגוריות ומוצרים - נתוני הלמ"ס
        </p>
      </div>

      {/* Business Insight */}
      <BusinessInsight
        title="אופטימיזציית תמהיל מוצרים"
        insight={`קטגוריית ${topCategory.category} מובילה בהכנסות עם ${formatNumber(topCategory.transaction_count)} עסקאות ונתח שוק של ${parseFloat(topCategory.market_share_pct).toFixed(1)}%.`}
        action="אסטרטגיה: התמקד בקטגוריות מובילות תוך פיתוח קטגוריות נישה עם מרווח גבוה למקסום רווחיות כוללת."
        color="purple"
        icon="📦"
      />

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="קטגוריה מובילה"
            description={`${topCategory.category} מייצרת את ההכנסות הגבוהות ביותר`}
            metric={formatCurrency(parseFloat(topCategory.total_revenue))}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="מגוון קטגוריות"
            description={`${categoriesData.categories.length} קטגוריות פעילות בשוק`}
            metric={categoriesData.categories.length.toString()}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="סך הכנסות"
            description="סך כל ההכנסות מכל הקטגוריות"
            metric={formatCurrency(totalRevenue)}
            type="success"
          />
        </div>
      </div>

      {/* Top 10 Categories Cards */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">Top 10 קטגוריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {categoriesData.categories.slice(0, 10).map((category, index) => (
            <div key={index} className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0">
                  #{index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm mb-1 truncate" title={category.category}>
                    {category.category}
                  </h3>
                  <p className="text-xs text-muted-foreground mb-2">
                    {formatNumber(category.transaction_count)} עסקאות
                  </p>
                  <p className="text-lg font-bold text-primary">
                    {formatCurrency(parseFloat(category.total_revenue))}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {parseFloat(category.market_share_pct).toFixed(1)}% מהשוק
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות</h2>
        <DataTable data={categoriesData.categories} columns={columns} />
      </div>

      {/* Business Insights & Conclusions */}
      <div className="bg-gradient-to-br from-purple-50 to-violet-50 border-2 border-purple-200 rounded-lg p-6" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-purple-900 flex items-center gap-2">
          <span className="text-3xl">📦</span>
          תובנות עסקיות ומסקנות
        </h2>
        <div className="space-y-3 text-gray-800 leading-relaxed">
          <p className="text-base">
            <strong>דומיננטיות קטגורית ברורה:</strong> קטגוריית {topCategory.category} שולטת בשוק עם {parseFloat(topCategory.market_share_pct).toFixed(1)}% נתח שוק ו-{formatNumber(topCategory.transaction_count)} עסקאות, מה שהופך אותה לנדבך המרכזי של כל אסטרטגיה עסקית בתחום.
          </p>
          <p className="text-base">
            <strong>זנב ארוך של קטגוריות נישה:</strong> מעבר ל-Top 3 קטגוריות, קיימות {categoriesData.categories.length - 3} קטגוריות נוספות עם נתחי שוק קטנים יותר - ״הזנב הארוך״ הזה מהווה הזדמנות למיצוב ייחודי ומרווחים גבוהים.
          </p>
          <p className="text-base">
            <strong>פוטנציאל למכירות צולבות:</strong> עם {categoriesData.categories.length} קטגוריות פעילות וסך {formatCurrency(totalRevenue)} הכנסות, קיים פוטנציאל משמעותי להגדלת ערך סל קנייה ממוצע דרך המלצות חכמות והצעות bundle מותאמות אישית.
          </p>
          <p className="text-base">
            <strong>ריווחיות מול היקף:</strong> בעוד שקטגוריות מובילות מייצרות היקפי מכירות גבוהים, חשוב לנתח את מרווח הרווח בכל קטגוריה - לעיתים קטגוריות קטנות יותר מניבות ROI טוב יותר בשל תחרות נמוכה יותר ומחירי פרימיום.
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית:</strong> אמץ אסטרטגיית ״עוגן + נישה״ - השקע 60-70% מהמשאבים בקטגוריות מובילות לשמירה על נתח שוק, ו-30-40% בפיתוח קטגוריות נישה עם מרווח גבוה ופוטנציאל צמיחה, תוך מינוף טכנולוגיות recommendation למכירות צולבות.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Products;
