import { TrendingUp, AlertTriangle, Store } from 'lucide-react';
import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { BusinessInsight } from '@/components/BusinessInsight';
import { useRetailBattle } from '@/hooks/useCBSData';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useMemo } from 'react';

const Revenue = () => {
  const { data: retailBattle, isLoading, error } = useRetailBattle();

  // Transform data for stacked bar chart (convert to percentages)
  const chartData = useMemo(() => {
    if (!retailBattle) return [];
    return retailBattle.categories.map(cat => {
      const total = cat.total || 100;
      return {
        category: cat.category,
        supermarket: (cat.supermarket / total) * 100,
        local: (cat.local_market / total) * 100,
        butcher: (cat.butcher / total) * 100,
        bakery: (cat.bakery / total) * 100,
      };
    });
  }, [retailBattle]);

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

  if (error || !retailBattle) {
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
    info: Store,
  };

  // Table columns
  const columns = [
    {
      key: 'category' as const,
      label: 'קטגוריה',
      sortable: true
    },
    {
      key: 'supermarket' as const,
      label: 'סופרמרקט (%)',
      sortable: true,
      render: (value: number) => `${((value / 100) * 100).toFixed(1)}%`
    },
    {
      key: 'local_market' as const,
      label: 'שוק מקומי (%)',
      sortable: true,
      render: (value: number) => `${((value / 100) * 100).toFixed(1)}%`
    },
    {
      key: 'butcher' as const,
      label: 'קצבים (%)',
      sortable: true,
      render: (value: number) => `${((value / 100) * 100).toFixed(1)}%`
    },
    {
      key: 'bakery' as const,
      label: 'מאפיות (%)',
      sortable: true,
      render: (value: number) => `${((value / 100) * 100).toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">קרב הקמעונאות: מי שולט בשוק המזון?</h1>
        <p className="text-muted-foreground" dir="rtl">
          ניתוח נתח שוק לפי סוגי נקודות מכירה - 13 קטגוריות מזון, נתוני הלמ״ס 2022
        </p>
      </div>

      {/* Business Insight */}
      <BusinessInsight
        title="המהפכה השקטה: השווקים המקומיים מובילים"
        insight={`שווקים מקומיים שולטים ב-${retailBattle.local_share.toFixed(1)}% מהשוק, הרבה יותר מסופרמרקטים (${retailBattle.supermarket_share.toFixed(1)}%). הצרכן הישראלי עדיין מעדיף טריות ושירות אישי על נוחות.`}
        action="אסטרטגיה: אם אתה מזון טרי (ירקות, בשר) → פוקוס שווקים ומכולות שכונתיות. מזון מעובד → סופרמרקטים + אונליין."
        color="green"
        icon="🏪"
      />

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="מוביל: שווקים מקומיים"
            description={`${retailBattle.local_share.toFixed(1)}% נתח שוק`}
            metric={`פי ${(retailBattle.local_share / retailBattle.supermarket_share).toFixed(1)} מסופרמרקטים`}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="סופרמרקטים"
            description="נתח שוק בקטגוריות מזון"
            metric={`${retailBattle.supermarket_share.toFixed(1)}%`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.warning}
            title="קטגוריות מנותחות"
            description="13 קטגוריות מזון מנתוני הלמ״ס"
            metric={retailBattle.categories.length.toString()}
            type="info"
          />
        </div>
      </div>

      {/* Market Share by Store Type - Stacked Bar Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">נתח שוק לפי סוג נקודת מכירה</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          כל מוט = קטגוריית מזון אחת. צבעים = סוגי חנויות. גובה = 100% (כל הרכישות באותה קטגוריה).
        </p>

        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={chartData} margin={{ top: 20, right: 30, bottom: 100, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="category"
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 10 }}
            />
            <YAxis
              label={{ value: 'נתח שוק (%)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={(value: number, name: string) => {
                const labels: Record<string, string> = {
                  supermarket: 'סופרמרקט',
                  local: 'שוק מקומי',
                  butcher: 'קצבים',
                  bakery: 'מאפיות',
                };
                return [`${value.toFixed(1)}%`, labels[name] || name];
              }}
              contentStyle={{ direction: 'rtl' }}
            />
            <Legend
              formatter={(value: string) => {
                const labels: Record<string, string> = {
                  supermarket: 'סופרמרקט',
                  local: 'שוק מקומי',
                  butcher: 'קצבים',
                  bakery: 'מאפיות',
                };
                return labels[value] || value;
              }}
            />
            <Bar dataKey="supermarket" stackId="a" fill="#3b82f6" name="supermarket" />
            <Bar dataKey="local" stackId="a" fill="#22c55e" name="local" />
            <Bar dataKey="butcher" stackId="a" fill="#ef4444" name="butcher" />
            <Bar dataKey="bakery" stackId="a" fill="#f59e0b" name="bakery" />
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg" dir="rtl">
          <p className="text-sm font-semibold text-green-900 mb-2">💡 פרשנות הגרף:</p>
          <ul className="text-sm text-green-800 space-y-1 list-disc list-inside">
            <li><strong>ירוק גבוה:</strong> שווקים מקומיים שולטים (ירקות, פירות, מוצרי חלב טריים)</li>
            <li><strong>כחול גבוה:</strong> סופרמרקטים חזקים (מוצרי מזון מעובדים, מותגים)</li>
            <li><strong>אדום גבוה:</strong> קצבים מתמחים (בשר טרי, עופות)</li>
            <li><strong>כתום גבוה:</strong> מאפיות (לחם טרי, מאפים)</li>
          </ul>
        </div>
      </div>

      {/* Where Supermarkets Lose - Top 5 */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">איפה סופרמרקטים מפסידים? Top 5</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          הקטגוריות שבהן שווקים מקומיים מנצחים בגדול - הזדמנויות למיתוג ״טרי ומקומי״
        </p>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {retailBattle.supermarket_loses.slice(0, 5).map((category, index) => {
            const localWin = category.local_pct - category.supermarket_pct;
            return (
              <div key={index} className="bg-card rounded-lg border border-border p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                    #{index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-sm mb-2" dir="rtl" title={category.category}>
                      {category.category}
                    </h3>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between" dir="rtl">
                        <span className="text-muted-foreground">שוק מקומי:</span>
                        <span className="font-bold text-green-600">{category.local_pct.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between" dir="rtl">
                        <span className="text-muted-foreground">סופרמרקט:</span>
                        <span className="font-semibold text-blue-600">{category.supermarket_pct.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between" dir="rtl">
                        <span className="text-muted-foreground">יתרון מקומי:</span>
                        <span className="font-bold text-primary">+{localWin.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Full Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות - פירוט מלא</h2>
        <DataTable data={retailBattle.categories} columns={columns} />
      </div>

      {/* Business Insights & Conclusions */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-6" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-green-900 flex items-center gap-2">
          <span className="text-3xl">🏪</span>
          תובנות עסקיות ומסקנות - קרב הקמעונאות
        </h2>
        <div className="space-y-3 text-gray-800 leading-relaxed">
          <p className="text-base">
            <strong>טריות מנצחת נוחות:</strong> שווקים מקומיים ({retailBattle.local_share.toFixed(1)}%) שולטים בשוק המזון הישראלי על פני סופרמרקטים ({retailBattle.supermarket_share.toFixed(1)}%) - פער של פי {(retailBattle.local_share / retailBattle.supermarket_share).toFixed(1)}. הצרכן הישראלי מוכן לוותר על נוחות לטובת איכות ומחיר.
          </p>
          <p className="text-base">
            <strong>התמחות מנצחת:</strong> קצבים ({retailBattle.butcher_share.toFixed(1)}%) ומאפיות שכונתיות מוכיחים שהתמחות במוצר ספציפי עם שירות אישי יכולים לשרוד מול ענקיות קמעונאות - מודל עסקי שלא מת.
          </p>
          <p className="text-base">
            <strong>ירקות ופירות = המבצר המקומי:</strong> בקטגוריית תוצרת טרייה, שווקים מקומיים שולטים כמעט לחלוטין. כל ניסיון של סופרמרקטים לחדור לשם נכשל בגלל תפיסת ״לא טרי״ בקרב הציבור.
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית למותגים:</strong> אם אתה מוכר מזון טרי (ירקות, בשר, חלב) - התמקד בשווקים מקומיים, מכולות שכונתיות, וקצבים. השקע במיתוג ״טרי ומקומי״ ובלוגיסטיקה מהירה. אם אתה מזון מעובד - סופרמרקטים + אונליין הם הערוץ הראשי.
          </p>
          <p className="text-base">
            <strong>הזדמנות דיגיטלית:</strong> עם {retailBattle.local_share.toFixed(1)}% מהשוק בשווקים פיזיים קטנים, יש הזדמנות ענקית לדיגיטציה - פלטפורמת B2B שמחברת שווקים מקומיים למסעדות ולצרכנים (״שוק בכיס״) יכולה לשבש את השוק.
          </p>
          <p className="text-base">
            <strong>אזהרה לסופרמרקטים:</strong> המשך שליטת השווקים המקומיים מצביעה על כשל ארוך טווח של רשתות הקמעונאות בקטגוריית התוצרת הטרייה. צריך מהפך במודל - אולי פינות ״שוק בתוך הסופר״ עם מוצרים מקומיים?
          </p>
        </div>
      </div>
    </div>
  );
};

export default Revenue;
