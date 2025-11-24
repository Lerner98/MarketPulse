import { AlertTriangle } from 'lucide-react';
import { BusinessInsight } from '@/components/BusinessInsight';
import { useInequalityGap, useBurnRate, useFreshFoodBattle } from '@/hooks/useCBSDataV9';
import { useMemo } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Legend } from 'recharts';

const DashboardV9 = () => {
  // Fetch V9 strategic insights (REAL CBS DATA 2022)
  const { data: inequalityGap, isLoading: loadingInequality, error: errorInequality } = useInequalityGap();
  const { data: burnRate, isLoading: loadingBurn, error: errorBurn } = useBurnRate();
  const { data: freshFoodBattle, isLoading: loadingRetail, error: errorRetail } = useFreshFoodBattle();

  const isLoading = loadingInequality || loadingBurn || loadingRetail;
  const error = errorInequality || errorBurn || errorRetail;

  // Top 10 Inequality Items Bar Chart
  const inequalityBarData = useMemo(() => {
    if (!inequalityGap) return [];
    return inequalityGap.top_inequality.slice(0, 10).map(item => ({
      name: item.item_name.length > 30 ? item.item_name.substring(0, 30) + '...' : item.item_name,
      'Q5 (עשירים)': item.rich_spend,
      'Q1 (ענייים)': item.poor_spend,
      ratio: item.gap_ratio,
    }));
  }, [inequalityGap]);

  // Burn Rate Pie Chart
  const burnRatePieData = useMemo(() => {
    if (!burnRate) return [];
    return burnRate.pressure_segments.map(segment => ({
      name: segment.quintile,
      value: segment.burn_rate,
      interpretation: segment.interpretation,
    }));
  }, [burnRate]);

  // Fresh Food Battle Chart
  const retailBattleData = useMemo(() => {
    if (!freshFoodBattle) return [];
    // Combine both supermarket dominance and traditional strongholds
    const allCategories = [
      ...freshFoodBattle.supermarket_dominance.slice(0, 5),
      ...freshFoodBattle.traditional_strongholds.slice(0, 5),
    ];
    return allCategories.map(item => ({
      name: item.category.length > 25 ? item.category.substring(0, 25) + '...' : item.category,
      'רשתות שיווק': item.supermarket_chain_pct,
      'מסורתי (שווקים/קצבים)': item.traditional_pct,
      winner: item.winner,
    }));
  }, [freshFoodBattle]);

  // Loading state
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

  // Error state
  if (error || !inequalityGap || !burnRate || !freshFoodBattle) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
          <p className="text-muted-foreground text-sm" dir="rtl">
            {error?.message || 'לא נמצאו נתונים'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">לוח בקרה ראשי - תובנות אסטרטגיות V9</h1>
        <div className="space-y-1" dir="rtl">
          <p className="text-muted-foreground font-medium">
            ניתוח הוצאות משקי בית ישראליים - נתוני הלמ"ס 2022
          </p>
          <p className="text-sm text-muted-foreground">
            מבוסס על 528 קטגוריות הוצאה + 14 קטגוריות מזון × 8 סוגי חנויות
          </p>
        </div>
      </div>

      {/* INSIGHT 1: Inequality Gap */}
      <BusinessInsight
        title="פער אי-שוויון בהוצאות"
        insight={inequalityGap.insight}
        action={`הקטגוריות עם הפער הגדול ביותר: ${inequalityGap.top_inequality[0].item_name} (פי ${inequalityGap.top_inequality[0].gap_ratio.toFixed(1)})`}
        color="blue"
        icon="💰"
      />

      {/* Top 10 Inequality Categories Bar Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">
          10 הקטגוריות עם הפער הגדול ביותר - Q5 לעומת Q1
        </h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          קטגוריות בהן משקי בית עשירים הוציאו הרבה יותר ממשקי בית ענייים
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={inequalityBarData} layout="vertical" margin={{ top: 20, right: 30, left: 150, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" />
            <YAxis
              type="category"
              dataKey="name"
              width={140}
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '12px', direction: 'rtl' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
              formatter={(value: number) => `₪${value.toFixed(2)}`}
            />
            <Legend />
            <Bar dataKey="Q5 (עשירים)" fill="#10b981" />
            <Bar dataKey="Q1 (ענייים)" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* INSIGHT 2: Burn Rate */}
      <BusinessInsight
        title="לחץ פיננסי - אחוז ההוצאה מההכנסה"
        insight={burnRate.insight}
        action={`Q1 מוציאים ${burnRate.q1_burn_rate}% מההכנסה (לחץ כלכלי), Q5 מוציאים ${burnRate.q5_burn_rate}% (חוסכים ${(100 - burnRate.q5_burn_rate).toFixed(1)}%)`}
        color="orange"
        icon="🔥"
      />

      {/* Burn Rate Pie Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">
          אחוז הוצאה מהכנסה לפי רמות הכנסה (Burn Rate)
        </h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          כמה אחוזים מההכנסה הולכים להוצאות? Q1 מוציאים יותר ממה שמרוויחים, Q5 חוסכים
        </p>

        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={burnRatePieData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={(entry) => `${entry.name}: ${entry.value}%`}
              labelLine={true}
            >
              {burnRatePieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={['#ef4444', '#f97316', '#eab308', '#22c55e', '#10b981'][index]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
              formatter={(value: number, name: string, props: any) => [
                `${value}% - ${props.payload.interpretation}`,
                name,
              ]}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* INSIGHT 3: Fresh Food Battle */}
      <BusinessInsight
        title="קרב המזון הטרי - רשתות מול מסורתי"
        insight={freshFoodBattle.insight}
        action={`רשתות: ${freshFoodBattle.aggregate_shares.supermarket_total}%, מסורתי: ${freshFoodBattle.aggregate_shares.traditional_total}%`}
        color="green"
        icon="🛒"
      />

      {/* Retail Battle Bar Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4" dir="rtl">
          קרב המזון הטרי - איפה קונים ישראלים?
        </h2>
        <p className="text-sm text-muted-foreground mb-4" dir="rtl">
          רשתות שיווק מול שווקים/קצבים/חנויות מיוחדות - מי מנצח בכל קטגוריה?
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={retailBattleData} layout="vertical" margin={{ top: 20, right: 30, left: 130, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis type="number" stroke="hsl(var(--muted-foreground))" domain={[0, 100]} />
            <YAxis
              type="category"
              dataKey="name"
              width={120}
              stroke="hsl(var(--muted-foreground))"
              style={{ fontSize: '12px', direction: 'rtl' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
              formatter={(value: number) => `${value.toFixed(1)}%`}
            />
            <Legend />
            <Bar dataKey="רשתות שיווק" fill="#3b82f6" />
            <Bar dataKey="מסורתי (שווקים/קצבים)" fill="#22c55e" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DashboardV9;
