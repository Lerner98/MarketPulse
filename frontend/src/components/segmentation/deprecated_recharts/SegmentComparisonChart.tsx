import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { TrendingUp } from "lucide-react";
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// === INTERFACES ADDED (Full Definition) ===
interface SegmentComparisonData {
  segment_value: string;
  income: number;
  spending: number;
  burn_rate_pct: number;
  surplus_deficit: number;
  financial_status: string;
}

interface SegmentComparisonChartProps {
  data: SegmentComparisonData[];
  segmentType: string;
  isLoading?: boolean;
}
// ==========================================

export const SegmentComparisonChart = ({ data, segmentType, isLoading = false }: SegmentComparisonChartProps) => {
  // Format numbers for Hebrew locale
  const formatCurrency = (value: number) => {
    return `₪${(value / 1000).toFixed(0)}K`;
  };

  if (isLoading) {
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            טוען השוואת הכנסות והוצאות...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
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
            <TrendingUp className="h-5 w-5" />
            השוואת הכנסות והוצאות
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <p className="text-gray-500">אין נתונים זמינים</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Transform data for line chart - sort by segment value for proper progression
  const chartData = [...data]
    .sort((a, b) => {
      // Extract numbers from segment values for proper sorting (Q1, Q2, etc.)
      const numA = parseInt(a.segment_value.match(/\d+/)?.[0] || '0');
      const numB = parseInt(b.segment_value.match(/\d+/)?.[0] || '0');
      return numA - numB;
    })
    .map(item => ({
      name: translateSegmentCode(item.segment_value, segmentType),
      הכנסה: item.income,
      הוצאה: item.spending
    }));

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          השוואת הכנסות והוצאות - {SEGMENT_DISPLAY_MAP[segmentType]?.summaryTitle || segmentType}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={450}>
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 60, bottom: 120 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              angle={-45}
              textAnchor="end"
              height={100}
              interval={0}
              dy={10}
            />
            <YAxis
              tickFormatter={formatCurrency}
              dx={-5}
              label={{ value: 'סכום (₪)', angle: -90, position: 'insideLeft', dx: -20 }}
            />
            <Tooltip
              formatter={(value: number) => [`₪${value.toLocaleString('he-IL')}`, '']}
              contentStyle={{ direction: 'rtl' }}
            />
            <Legend
              wrapperStyle={{ direction: 'rtl', paddingTop: '10px' }}
            />
            <Line
              type="monotone"
              dataKey="הכנסה"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 7 }}
              label={false}
            />
            <Line
              type="monotone"
              dataKey="הוצאה"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 7 }}
              label={false}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Explanation */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded" dir="rtl">
          <p className="text-sm text-blue-800">
            <strong>💡 מה זה אומר?</strong> קו ירוק = הכנסה חודשית | קו כחול = הוצאה חודשית | הפער ביניהם מראה כמה כל קבוצה חוסכת או מוציאת יותר מהכנסתה
          </p>
        </div>
      </CardContent>
    </Card>
  );
};