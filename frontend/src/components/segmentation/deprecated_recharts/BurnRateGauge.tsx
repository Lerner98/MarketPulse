import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Gauge } from "lucide-react";
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// === INTERFACES (Full Definition) ===
interface BurnRateData {
  segment_value: string;
  income: number;
  spending: number;
  burn_rate_pct: number;
  surplus_deficit: number;
  financial_status: string;
}

interface BurnRateGaugeProps {
  data: BurnRateData[];
  segmentType: string;
  isLoading?: boolean;
}
// ===================================

export const BurnRateGauge = ({ data, segmentType, isLoading = false }: BurnRateGaugeProps) => {
  // Only show for income-based segments
  const isIncomeSegment = segmentType === "Income Quintile" || segmentType === "Income Decile (Net)" || segmentType === "Income Decile (Gross)";

  if (!isIncomeSegment) {
    return null; // Don't render for non-income segments
  }

  if (isLoading) {
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            טוען ניתוח יחס הוצאה-הכנסה...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-gray-500">טוען...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            יחס הוצאה-הכנסה
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-gray-500">אין נתונים זמינים</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Transform data for pie chart - each segment is a slice
  const pieData = data.map((item) => ({
    name: item.segment_value,
    value: item.burn_rate_pct,
    fullData: item
  }));

  // Color coding: Red (>100%), Amber (90-100%), Green (<90%)
  const getColor = (burnRate: number) => {
    if (burnRate > 100) return "#ef4444"; // Red - overspending
    if (burnRate > 90) return "#f59e0b"; // Amber - warning
    return "#10b981"; // Green - healthy
  };

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="h-5 w-5" />
          יחס הוצאה-הכנסה
        </CardTitle>
        {/* ACTION: CardDescription DELETED (Redundancy Fix) */}
      </CardHeader>
      <CardContent>
        {/* Color Legend */}
        <div className="mb-4 flex gap-4 justify-center text-sm" dir="rtl">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>{"<"}90% בריא</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <span>90-100% אזהרה</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>{">"}100% חריגה</span>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={320}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="45%"
              labelLine={{stroke: '#666', strokeWidth: 1}}
              // ACTION: Clean Label - only displays percentage, suppresses segment index/name
              label={({ value }: { value: number }) => `${value.toFixed(1)}%`} 
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.value)} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload.fullData as BurnRateData;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded shadow-lg" dir="rtl">
                      <p className="font-semibold mb-2">{item.segment_value}</p>
                      <p className="text-sm text-green-700">
                        הכנסה: ₪{item.income.toLocaleString('he-IL')}
                      </p>
                      <p className="text-sm text-blue-700">
                        הוצאה: ₪{item.spending.toLocaleString('he-IL')}
                      </p>
                      <p className={`text-sm font-semibold mt-1 ${
                        item.burn_rate_pct > 100 ? 'text-red-700' :
                        item.burn_rate_pct > 90 ? 'text-amber-700' : 'text-green-700'
                      }`}>
                        {item.burn_rate_pct.toFixed(1)}% מההכנסה
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        {item.surplus_deficit >= 0
                          ? `✅ עודף: ₪${item.surplus_deficit.toLocaleString('he-IL')}`
                          : `⚠️ גירעון: ₪${Math.abs(item.surplus_deficit).toLocaleString('he-IL')}`
                        }
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Explanation */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded" dir="rtl">
          <p className="text-sm text-blue-800">
            <strong>💡 מה זה אומר?</strong> קבוצות ירוקות חוסכות כסף מדי חודש | קבוצות אדומות מוציאות יותר מההכנסה (סמן לחוב או תמיכה חיצונית)
          </p>
        </div>
      </CardContent>
    </Card>
  );
};