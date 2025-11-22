import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { BusinessInsight } from '@/components/BusinessInsight';
import { formatCurrency } from '@/lib/utils/hebrew';
import { Users, TrendingUp, Lightbulb, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { useQuintileGap } from '@/hooks/useCBSData';
import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Customers = () => {
  const { data: quintileGap, isLoading, error } = useQuintileGap();

  // Calculate totals for all quintiles
  const quintileTotals = useMemo(() => {
    if (!quintileGap) return [];

    const q2Total = quintileGap.categories.reduce((sum, c) => sum + c.quintile_2, 0);
    const q3Total = quintileGap.categories.reduce((sum, c) => sum + c.quintile_3, 0);
    const q4Total = quintileGap.categories.reduce((sum, c) => sum + c.quintile_4, 0);

    const grandTotal = quintileGap.q1_total + q2Total + q3Total + q4Total + quintileGap.q5_total;

    return [
      {
        quintile: 1,
        label: 'Q1 - הכנסה נמוכה',
        total: quintileGap.q1_total,
        percentage: (quintileGap.q1_total / grandTotal) * 100,
        color: '#ef4444'
      },
      {
        quintile: 2,
        label: 'Q2',
        total: q2Total,
        percentage: (q2Total / grandTotal) * 100,
        color: '#f97316'
      },
      {
        quintile: 3,
        label: 'Q3',
        total: q3Total,
        percentage: (q3Total / grandTotal) * 100,
        color: '#eab308'
      },
      {
        quintile: 4,
        label: 'Q4',
        total: q4Total,
        percentage: (q4Total / grandTotal) * 100,
        color: '#22c55e'
      },
      {
        quintile: 5,
        label: 'Q5 - הכנסה גבוהה',
        total: quintileGap.q5_total,
        percentage: (quintileGap.q5_total / grandTotal) * 100,
        color: '#10b981'
      },
    ];
  }, [quintileGap]);

  const totalSpending = useMemo(() => {
    return quintileTotals.reduce((sum, q) => sum + q.total, 0);
  }, [quintileTotals]);

  const avgSpending = totalSpending / 5;

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

  if (error || !quintileGap) {
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

  // Prepare top 10 categories sorted by Q5 spending
  const topCategories = [...quintileGap.categories]
    .sort((a, b) => b.quintile_5 - a.quintile_5)
    .slice(0, 10);

  // Table columns for top categories
  const columns = [
    {
      key: 'category' as const,
      label: 'קטגוריה',
      sortable: true
    },
    {
      key: 'quintile_1' as const,
      label: 'Q1 (₪)',
      sortable: true,
      render: (value: number) => formatCurrency(value)
    },
    {
      key: 'quintile_3' as const,
      label: 'Q3 (₪)',
      sortable: true,
      render: (value: number) => formatCurrency(value)
    },
    {
      key: 'quintile_5' as const,
      label: 'Q5 (₪)',
      sortable: true,
      render: (value: number) => formatCurrency(value)
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ניתוח לפי רמות הכנסה</h1>
        <p className="text-muted-foreground" dir="rtl">
          דפוסי הוצאה של משקי בית לפי 5 רמות הכנסה - 88 קטגוריות, נתוני הלמ״ס 2022
        </p>
      </div>

      {/* Business Insight */}
      <BusinessInsight
        title="אסטרטגיית סגמנטציה"
        insight={`${quintileGap.insight} - פער של פי ${quintileGap.ratio} בין משקי בית עשירים (Q5) לעניים (Q1).`}
        action="השקע משאבי שירות ושיווק ברמות הכנסה Q4-Q5 - ה-LTV שלהם גבוה משמעותית מהממוצע. פתח מוצרי פרימיום לרמות אלו."
        color="green"
        icon="🎯"
      />

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          icon={Users}
          title="סך הוצאות (כל הרמות)"
          value={formatCurrency(totalSpending)}
          iconColor="bg-primary/10 text-primary"
        />
        <MetricCard
          icon={Users}
          title="ממוצע לרמת הכנסה"
          value={formatCurrency(avgSpending)}
          iconColor="bg-secondary/10 text-secondary"
        />
        <MetricCard
          icon={Users}
          title={`פער Q5/Q1`}
          value={`פי ${quintileGap.ratio}`}
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
            description={`Q5 הוציאו ${formatCurrency(quintileGap.q5_total)} לעומת ${formatCurrency(quintileGap.q1_total)} ב-Q1`}
            metric={`פער של פי ${quintileGap.ratio}`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.info}
            title="הכנסה גבוהה (Q5)"
            description="משקי בית ברמת הכנסה הגבוהה ביותר"
            metric={`${quintileTotals[4]?.percentage.toFixed(1)}% מהשוק`}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="הכנסה נמוכה (Q1)"
            description="משקי בית ברמת הכנסה נמוכה"
            metric={`${quintileTotals[0]?.percentage.toFixed(1)}% מהשוק`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="רמות הכנסה בינוניות"
            description="רמות Q2-Q4 מהוות את רוב השוק"
            metric={`${(quintileTotals[1]?.percentage + quintileTotals[2]?.percentage + quintileTotals[3]?.percentage).toFixed(1)}%`}
            type="success"
          />
        </div>
      </div>

      {/* Spending Distribution by Income Level - Bar Chart (REAL CBS DATA) */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">התפלגות הוצאות לפי רמות הכנסה (88 קטגוריות)</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          סך הוצאות בכל רמת הכנסה על פני 88 קטגוריות מוצרים. גובה המוט = סך ההוצאה החודשית הממוצעת.
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={quintileTotals} margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="label"
              angle={-15}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              label={{ value: 'סך הוצאות (₪)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
              tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip
              formatter={(value: number) => [`₪${value.toLocaleString('he-IL')}`, 'סך הוצאות']}
              labelStyle={{ textAlign: 'right', direction: 'rtl' }}
              contentStyle={{ direction: 'rtl' }}
            />
            <Bar dataKey="total" radius={[8, 8, 0, 0]}>
              {quintileTotals.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg" dir="rtl">
          <p className="text-sm font-semibold text-green-900 mb-2">📈 תובנה:</p>
          <p className="text-sm text-green-800">
            משקי בית עשירים (Q5) מוציאים {formatCurrency(quintileGap.q5_total)} לעומת {formatCurrency(quintileGap.q1_total)} במשקי בית ענייים (Q1) -
            פער של פי {quintileGap.ratio}. זה לא רק הבדל בכוח קנייה, אלא הזדמנות עסקית: פתח מוצרי פרימיום עם מרווח גבוה ל-Q4-Q5.
          </p>
        </div>
      </div>

      {/* Top 10 Categories by Q5 Spending (REAL CBS DATA) */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">Top 10 קטגוריות - הוצאות Q5 (עשירים)</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          הקטגוריות שמשקי בית עשירים מוציאים בהן הכי הרבה - הזדמנויות למוצרי פרימיום
        </p>
        <DataTable data={topCategories} columns={columns} />
      </div>

      {/* Distribution Visualization */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <h2 className="col-span-full text-xl font-semibold mb-2" dir="rtl">
          פירוט לפי רמות הכנסה - 88 קטגוריות
        </h2>
        {quintileTotals.map((quintile) => (
          <div key={quintile.quintile} className="bg-card rounded-lg border border-border p-4">
            <div className="text-center">
              <div className="text-sm font-semibold text-primary mb-2">
                {quintile.label}
              </div>
              <div className="text-2xl font-bold mb-1">
                {formatCurrency(quintile.total)}
              </div>
              <div className="text-xs text-muted-foreground">
                88 קטגוריות
              </div>
              <div className="text-xs text-primary mt-2">
                {quintile.percentage.toFixed(1)}% מהשוק
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Business Insights & Conclusions */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-6" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-green-900 flex items-center gap-2">
          <span className="text-3xl">🎯</span>
          תובנות עסקיות ומסקנות - אסטרטגיית סגמנטציה
        </h2>
        <div className="space-y-3 text-gray-800 leading-relaxed">
          <p className="text-base">
            <strong>פער דרמטי בהוצאה:</strong> ניתוח 88 קטגוריות מוצרים מראה שמשקי בית עשירים (Q5) הוציאו {formatCurrency(quintileGap.q5_total)} לעומת {formatCurrency(quintileGap.q1_total)} במשקי בית ענייים (Q1) - פער של פי {quintileGap.ratio}. זה לא רק סטטיסטיקה, זה מפת דרכים לתמחור ומיצוב.
          </p>
          <p className="text-base">
            <strong>ריכוזיות כלכלית:</strong> רמות ההכנסה הגבוהות (Q4-Q5) מייצרות {(quintileTotals[3]?.percentage + quintileTotals[4]?.percentage).toFixed(1)}% מסך ההוצאות למרות היותן רק 40% מהאוכלוסייה - עקרון פארטו (80/20) מאומת בשוק הישראלי.
          </p>
          <p className="text-base">
            <strong>השוק האמצעי לא נעלם:</strong> רמות Q2-Q4 מהוות ביחד {(quintileTotals[1]?.percentage + quintileTotals[2]?.percentage + quintileTotals[3]?.percentage).toFixed(1)}% מהשוק - קהל יעד גדול ויציב. אל תזניח אותו לטובת הקצוות בלבד.
          </p>
          <p className="text-base">
            <strong>LTV מבוסס נתונים:</strong> לקוח מ-Q5 שווה פי {quintileGap.ratio} מלקוח מ-Q1 - עובדה שצריכה להשפיע על תקציב רכישת הלקוחות (CAC). מותר (ואפילו כדאי) להשקיע יותר ברכישת לקוחות Q4-Q5.
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית #1:</strong> פתח שלוש קווי מוצרים נפרדים - ״פרימיום״ ל-Q4-Q5 (דגש על איכות, שירות VIP, תמחור גבוה), ״ערך״ ל-Q2-Q3 (יחס מחיר-ביצוע מעולה, נגישות), ו״בסיסי״ ל-Q1 (מחיר תחרותי מקסימלי).
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית #2:</strong> השתמש בנתוני הפער הקטגוריאליים לתמחור דינמי - קטגוריות עם פער גבוה (דיור, תחבורה) מצביעות על נכונות לשלם (WTP) גבוהה יותר ברמות הכנסה עליונות.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Customers;
