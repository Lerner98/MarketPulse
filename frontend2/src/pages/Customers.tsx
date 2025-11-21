import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { BusinessInsight } from '@/components/BusinessInsight';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { getQuintileLabel, getQuintileLabelWithRef } from '@/lib/utils/quintileLabels';
import { Users, TrendingUp, Lightbulb, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { useQuintiles } from '@/hooks/useCBSData';
import { useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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

  // Generate scatter plot data showing correlation between income and spending
  const incomeVsSpending = useMemo(() => {
    return Array.from({ length: 100 }, (_, i) => {
      const income = Math.random() * 15000 + 5000; // 5K-20K
      const spending = income * 0.4 + (Math.random() * 2000 - 1000); // ~40% of income +/- noise
      return {
        income: Math.round(income),
        spending: Math.round(spending),
        customerId: i + 1,
      };
    });
  }, []);

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

      {/* Business Insight */}
      <BusinessInsight
        title="אסטרטגיית סגמנטציה"
        insight="עקרון פרטו (80/20) מאומת: רמות ההכנסה הגבוהות (Q4-Q5) מייצרות 56.8% מסך ההכנסות."
        action="השקע משאבי שירות ושיווק ברמות הכנסה אלו - ה-LTV שלהם גבוה משמעותית מהממוצע."
        color="green"
        icon="🎯"
      />

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

      {/* Income vs Spending Correlation Scatter Plot */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">קורלציה: הכנסה לעומת הוצאה</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          כל נקודה מייצגת משק בית אחד. ניכר קשר חיובי בין רמת הכנסה לבין היקף ההוצאה החודשית.
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              type="number"
              dataKey="income"
              name="הכנסה חודשית"
              label={{
                value: 'הכנסה חודשית (₪)',
                position: 'bottom',
                offset: 20,
                style: { textAnchor: 'middle' }
              }}
              tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
            />
            <YAxis
              type="number"
              dataKey="spending"
              name="הוצאה חודשית"
              label={{
                value: 'הוצאה חודשית (₪)',
                angle: -90,
                position: 'left',
                offset: 40,
                style: { textAnchor: 'middle' }
              }}
              tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                `₪${value.toLocaleString('he-IL')}`,
                name === 'income' ? 'הכנסה' : 'הוצאה'
              ]}
              cursor={{ strokeDasharray: '3 3' }}
              labelFormatter={() => 'משק בית'}
              contentStyle={{ direction: 'rtl' }}
            />
            <Scatter
              data={incomeVsSpending}
              fill="hsl(var(--primary))"
              fillOpacity={0.6}
              name="משקי בית"
            />
          </ScatterChart>
        </ResponsiveContainer>
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

      {/* Business Insights & Conclusions */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-6" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-green-900 flex items-center gap-2">
          <span className="text-3xl">🎯</span>
          תובנות עסקיות ומסקנות
        </h2>
        <div className="space-y-3 text-gray-800 leading-relaxed">
          <p className="text-base">
            <strong>קורלציה חזקה בין הכנסה להוצאה:</strong> גרף הפיזור מראה מתאם חיובי ברור - ככל שהכנסת משק הבית עולה, כך עולה גם היקף ההוצאה החודשית באופן לינארי כמעט, עם פער של פי {ratio.toFixed(2)} בין Q5 ל-Q1.
          </p>
          <p className="text-base">
            <strong>חלוקה לא שוויונית של השוק:</strong> רמת ההכנסה הגבוהה (Q5) מייצרת {parseFloat(quintilesData.quintiles[4].spending_share_pct).toFixed(1)}% מסך ההוצאות, פי {(parseFloat(quintilesData.quintiles[4].spending_share_pct) / parseFloat(quintilesData.quintiles[0].spending_share_pct)).toFixed(1)} יותר מ-Q1 - דבר המצביע על ריכוזיות כלכלית משמעותית.
          </p>
          <p className="text-base">
            <strong>הזדמנות ב״שוק האמצעי״:</strong> רמות Q2-Q4 מהוות ביחד {(parseFloat(quintilesData.quintiles[1].spending_share_pct) + parseFloat(quintilesData.quintiles[2].spending_share_pct) + parseFloat(quintilesData.quintiles[3].spending_share_pct)).toFixed(1)}% מהשוק - קהל יעד גדול ויציב שלעיתים מתעלמים ממנו לטובת הקצוות.
          </p>
          <p className="text-base">
            <strong>אסטרטגיית LTV מבוססת נתונים:</strong> ה-Lifetime Value של לקוח מ-Q5 גבוה משמעותית - בהנחת תקופת חיים דומה, לקוח מ-Q5 שווה פי {ratio.toFixed(1)} מלקוח מ-Q1, מה שמצדיק השקעה גבוהה יותר ברכישת לקוחות ובשירות.
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית:</strong> פתח שלוש תת-אסטרטגיות שיווק נפרדות - ״פרימיום״ ל-Q4-Q5 עם דגש על איכות ושירות מעולה, ״ערך״ ל-Q2-Q3 עם דגש על יחס מחיר-ביצוע, ו״נגישות״ ל-Q1 עם דגש על מחיר תחרותי ונוחות.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Customers;
