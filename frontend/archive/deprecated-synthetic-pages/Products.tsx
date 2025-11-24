import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { BusinessInsight } from '@/components/BusinessInsight';
import { formatNumber } from '@/lib/utils/hebrew';
import { TrendingUp, Lightbulb, AlertTriangle, Package } from 'lucide-react';
import { useDigitalMatrix } from '@/hooks/useCBSData';
import { useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Products = () => {
  const { data: digitalMatrix, isLoading, error } = useDigitalMatrix();

  // Scatter plot data: Israel Online % vs Abroad Online %
  const scatterData = useMemo(() => {
    if (!digitalMatrix) return [];
    return digitalMatrix.categories.map(cat => ({
      category: cat.category,
      israelOnline: cat.online_israel_pct,
      abroadOnline: cat.online_abroad_pct,
      physical: cat.physical_pct,
    }));
  }, [digitalMatrix]);

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

  if (error || !digitalMatrix) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
          <p className="text-muted-foreground text-sm" dir="rtl">
            {error?.message}
          </p>
        </div>
      </div>
    );
  }

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  // Top digital product
  const topDigital = digitalMatrix.top_israel_online[0];

  const columns = [
    {
      key: 'category' as const,
      label: 'קטגוריה',
      sortable: true
    },
    {
      key: 'physical_pct' as const,
      label: 'רכישה פיזית (%)',
      sortable: true,
      render: (value: number) => `${value.toFixed(1)}%`
    },
    {
      key: 'online_israel_pct' as const,
      label: 'אונליין ישראל (%)',
      sortable: true,
      render: (value: number) => `${value.toFixed(1)}%`
    },
    {
      key: 'online_abroad_pct' as const,
      label: 'אונליין חו"ל (%)',
      sortable: true,
      render: (value: number) => `${value.toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">מטריצת ההזדמנויות הדיגיטלית</h1>
        <p className="text-muted-foreground" dir="rtl">
          ניתוח דפוסי רכישה: פיזי מול דיגיטלי - נתוני הלמ״ס 2022
        </p>
      </div>

      {/* Business Insight */}
      <BusinessInsight
        title="אסטרטגיית E-Commerce: איפה לפתוח חנות אונליין?"
        insight={`${topDigital.category} מוביל ברכישות אונליין בישראל עם ${topDigital.online_israel_pct.toFixed(1)}% מהשוק הדיגיטלי.`}
        action="אסטרטגיה: מוצרים דיגיטליים (תוכנות, משחקים) → פוקוס אונליין. מוצרים פיזיים גדולים (רהיטים) → שילוב showroom + דיגיטל."
        color="purple"
        icon="🛒"
      />

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="מוביל דיגיטלי - ישראל"
            description={`${topDigital.category}`}
            metric={`${topDigital.online_israel_pct.toFixed(1)}%`}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title='מוביל דיגיטלי - חו"ל'
            description={`${digitalMatrix.top_abroad_online[0].category}`}
            metric={`${digitalMatrix.top_abroad_online[0].online_abroad_pct.toFixed(1)}%`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="קטגוריות מנותחות"
            description="55 קטגוריות מוצרים מנתוני הלמ״ס"
            metric={digitalMatrix.categories.length.toString()}
            type="success"
          />
        </div>
      </div>

      {/* Digital Opportunity Scatter Plot */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">מטריצת ההזדמנויות: אונליין ישראל מול חו״ל</h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          כל נקודה = קטגוריית מוצר. ימין למעלה = פוטנציאל דיגיטלי גבוה (ישראל + חו״ל), שמאל למטה = עדיין פיזי.
        </p>

        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              type="number"
              dataKey="israelOnline"
              name="אונליין ישראל (%)"
              label={{
                value: 'אונליין ישראל (%)',
                position: 'bottom',
                offset: 40,
                style: { textAnchor: 'middle' }
              }}
              domain={[0, 100]}
            />
            <YAxis
              type="number"
              dataKey="abroadOnline"
              name='אונליין חו"ל (%)'
              label={{
                value: 'אונליין חו"ל (%)',
                angle: -90,
                position: 'left',
                offset: 40,
                style: { textAnchor: 'middle' }
              }}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                `${value.toFixed(1)}%`,
                name === 'israelOnline' ? 'אונליין ישראל' : 'אונליין חו"ל'
              ]}
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ direction: 'rtl' }}
            />
            <Legend />
            <Scatter
              data={scatterData}
              fill="hsl(var(--primary))"
              fillOpacity={0.7}
              name="קטגוריות מוצרים"
            />
          </ScatterChart>
        </ResponsiveContainer>

        <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg" dir="rtl">
          <p className="text-sm font-semibold text-purple-900 mb-2">💡 פרשנות המטריצה:</p>
          <ul className="text-sm text-purple-800 space-y-1 list-disc list-inside">
            <li><strong>רבע ימני עליון:</strong> פוטנציאל דיגיטלי גבוה (תוכנות, גאדג&apos;טים) → השקעה מלאה באונליין</li>
            <li><strong>רבע שמאלי תחתון:</strong> עדיין פיזי (רהיטים, מזון טרי) → showroom פיזי + אונליין תומך</li>
            <li><strong>אמצע:</strong> מעבר הדרגתי → מודל היברידי (click &amp; collect, virtual try-on)</li>
          </ul>
        </div>
      </div>

      {/* Top 10 Digital Leaders */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">Top 10 קטגוריות דיגיטליות (אונליין ישראל)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {digitalMatrix.top_israel_online.slice(0, 10).map((category, index) => (
            <div key={index} className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0">
                  #{index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm mb-1" dir="rtl" title={category.category}>
                    {category.category}
                  </h3>
                  <p className="text-lg font-bold text-primary">
                    {category.online_israel_pct.toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    אונליין ישראל
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות - מטריצה מלאה</h2>
        <DataTable data={digitalMatrix.categories} columns={columns} />
      </div>

      {/* Business Insights & Conclusions */}
      <div className="bg-gradient-to-br from-purple-50 to-violet-50 border-2 border-purple-200 rounded-lg p-6" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-purple-900 flex items-center gap-2">
          <span className="text-3xl">🛒</span>
          תובנות עסקיות ומסקנות - המהפכה הדיגיטלית
        </h2>
        <div className="space-y-3 text-gray-800 leading-relaxed">
          <p className="text-base">
            <strong>דיגיטל מנצח בתוכנות ומשחקים:</strong> קטגוריית &quot;תוכנות, משחקי מחשב&quot; מובילה ב-{topDigital.online_israel_pct.toFixed(1)}% רכישות אונליין בישראל - ברור שמוצרים דיגיטליים טהורים הם המועמדים המושלמים למסחר אלקטרוני ללא פשרות.
          </p>
          <p className="text-base">
            <strong>פער ישראל-חו&quot;ל מגלה הזדמנויות:</strong> קטגוריות עם אחוזי חו&quot;ל גבוהים (כמו {digitalMatrix.top_abroad_online[0].category} ב-{digitalMatrix.top_abroad_online[0].online_abroad_pct.toFixed(1)}%) מצביעות על מחסור בהיצע מקומי - הזדמנות לעסקים ישראליים למלא את הפער ולהחזיר קונים הביתה.
          </p>
          <p className="text-base">
            <strong>הפיזי לא מת - רק משתנה:</strong> קטגוריות עם אחוזי &quot;פיזי&quot; גבוהים (רהיטים, מזון טרי) מראות שחלק מהמוצרים דורש חוויה מוחשית - האסטרטגיה הנכונה היא מודל omnichannel (showroom + אונליין) ולא נטישת הפיזי לחלוטין.
          </p>
          <p className="text-base">
            <strong>הזנב הארוך הדיגיטלי:</strong> עם 55 קטגוריות מנותחות, ניכר כי גם מוצרים ״לא-דיגיטליים״ מסורתיים מתחילים לעבור לרכישה מקוונת - מגמה שתתחזק, במיוחד עם שיפור לוגיסטיקה ומשלוחים.
          </p>
          <p className="text-base">
            <strong>המלצה אסטרטגית:</strong> בנה מטריצת החלטות: (1) מוצרים דיגיטליים טהורים → 100% אונליין, (2) מוצרים קטנים/זולים → אונליין עם משלוחים מהירים, (3) מוצרים גדולים/יקרים → מודל היברידי (browse online, experience in-store, buy anywhere), (4) מזון טרי → quick commerce (משלוחים תוך שעתיים).
          </p>
        </div>
      </div>
    </div>
  );
};

export default Products;
