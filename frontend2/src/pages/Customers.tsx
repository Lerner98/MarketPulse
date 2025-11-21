import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { getQuintileLabel, getQuintileLabelWithRef } from '@/lib/utils/quintileLabels';
import { Users, TrendingUp, Lightbulb, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { useQuintiles } from '@/hooks/useCBSData';

const Customers = () => {
  const { data: quintilesData, isLoading, error } = useQuintiles();

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

  if (error || !quintilesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
        </div>
      </div>
    );
  }

  const totalTransactions = quintilesData.quintiles.reduce(
    (sum, q) => sum + q.transaction_count,
    0
  );

  const totalSpent = quintilesData.quintiles.reduce(
    (sum, q) => sum + parseFloat(q.total_spending),
    0
  );

  const avgSpentPerQuintile = totalSpent / 5;

  // Calculate Q5 to Q1 ratio
  const q5Avg = parseFloat(quintilesData.quintiles[4].avg_transaction);
  const q1Avg = parseFloat(quintilesData.quintiles[0].avg_transaction);
  const ratio = q5Avg / q1Avg;

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  const columns = [
    {
      key: 'income_quintile' as const,
      label: 'רמת הכנסה',
      sortable: true,
      render: (value: number) => getQuintileLabelWithRef(value)
    },
    {
      key: 'transaction_count' as const,
      label: 'מספר עסקאות',
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    {
      key: 'total_spending' as const,
      label: 'סך הוצאה',
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
    {
      key: 'spending_share_pct' as const,
      label: 'נתח שוק',
      sortable: true,
      render: (value: string) => `${parseFloat(value).toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ניתוח לפי רמות הכנסה</h1>
        <p className="text-muted-foreground" dir="rtl">
          דפוסי הוצאה של משקי בית לפי 5 רמות הכנסה - נתוני הלמ"ס
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          icon={Users}
          title="סך עסקאות"
          value={formatNumber(totalTransactions)}
          iconColor="bg-primary/10 text-primary"
        />
        <MetricCard
          icon={Users}
          title="סך הוצאות"
          value={formatCurrency(totalSpent)}
          iconColor="bg-secondary/10 text-secondary"
        />
        <MetricCard
          icon={Users}
          title="ממוצע לרמת הכנסה"
          value={formatCurrency(avgSpentPerQuintile)}
          iconColor="bg-accent/10 text-accent"
        />
      </div>

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="פער הכנסות"
            description={quintilesData.key_insight}
            metric={`פער של ${ratio.toFixed(2)}x`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.info}
            title="הכנסה גבוהה (Q5)"
            description="משקי בית ברמת הכנסה הגבוהה ביותר"
            metric={`${parseFloat(quintilesData.quintiles[4].spending_share_pct).toFixed(1)}% מהשוק`}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="הכנסה נמוכה (Q1)"
            description="משקי בית ברמת הכנסה נמוכה"
            metric={`${parseFloat(quintilesData.quintiles[0].spending_share_pct).toFixed(1)}% מהשוק`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="רמות הכנסה בינוניות"
            description="רמות Q2-Q4 מהוות את רוב השוק"
            metric={`${(
              parseFloat(quintilesData.quintiles[1].spending_share_pct) +
              parseFloat(quintilesData.quintiles[2].spending_share_pct) +
              parseFloat(quintilesData.quintiles[3].spending_share_pct)
            ).toFixed(1)}%`}
            type="success"
          />
        </div>
      </div>

      {/* Quintiles Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">פירוט לפי רמות הכנסה</h2>
        <DataTable data={quintilesData.quintiles} columns={columns} />
      </div>

      {/* Distribution Visualization */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <h2 className="col-span-full text-xl font-semibold mb-2" dir="rtl">
          התפלגות הוצאות לפי רמות הכנסה
        </h2>
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
                {formatNumber(quintile.transaction_count)} עסקאות
              </div>
              <div className="text-xs text-primary mt-2">
                ממוצע: {formatCurrency(parseFloat(quintile.avg_transaction))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Customers;
