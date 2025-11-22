import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { BarChart3 } from "lucide-react";
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// === INTERFACES ADDED (Full Definition) ===
interface CategoryComparisonData {
  segment_value: string;
  income: number;
  spending: number;
  burn_rate_pct: number;
  surplus_deficit: number;
  financial_status: string;
}

interface CategoryComparisonChartProps {
  data: CategoryComparisonData[];
  segmentType: string;
  isLoading?: boolean;
}
// ==========================================

// Professional color palette for different categories
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

export const CategoryComparisonChart = ({ data, segmentType, isLoading = false }: CategoryComparisonChartProps) => {
  // ACTION: Debugging log added to check data arrival
  console.log('CategoryComparisonChart - Data received:', data);
  console.log('CategoryComparisonChart - Segment type:', segmentType);

  const formatCurrency = (value: number) => {
    return `₪${(value / 1000).toFixed(0)}K`;
  };

  if (isLoading) {
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            טוען השוואת קבוצות...
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
            <BarChart3 className="h-5 w-5" />
            השוואת קבוצות
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

  // Transform data for horizontal bar chart - sort by spending descending
  const chartData = [...data]
    .filter(item => item && item.segment_value) // CRITICAL FIX: Filter out null/undefined segments
    .sort((a, b) => b.spending - a.spending)
    .map((item, index) => ({
      name: translateSegmentCode(String(item.segment_value), segmentType), // CRITICAL FIX: Translate CBS codes to Hebrew labels
      הכנסה: item.income || 0,
      הוצאה: item.spending || 0,
      עודף_גרעון: item.surplus_deficit || 0,
      color: COLORS[index % COLORS.length]
    }));

  // ACTION: Debug transformed data
  console.log('CategoryComparisonChart - Transformed chartData:', chartData);
  console.log('CategoryComparisonChart - chartData length:', chartData.length);
  console.log('CategoryComparisonChart - First item:', chartData[0]);

  // Check if chartData is empty after transformation
  if (chartData.length === 0) {
    console.error('CategoryComparisonChart - chartData is EMPTY after transformation!');
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            השוואת קבוצות
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px] flex items-center justify-center">
            <p className="text-red-500">שגיאה: נתונים התקבלו ({data.length} פריטים) אך נכשלו בעיבוד</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Dynamic height based on number of categories
  const chartHeight = Math.max(400, chartData.length * 60);

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          השוואת הכנסות והוצאות - {SEGMENT_DISPLAY_MAP[segmentType]?.summaryTitle || segmentType}
        </CardTitle>
        {/* ACTION: CardDescription DELETED (Redundancy Fix) */}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart
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
            <Bar dataKey="הכנסה" fill="#10b981" />
            <Bar dataKey="הוצאה" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>

        {/* Explanation */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded" dir="rtl">
          <p className="text-sm text-blue-800">
            <strong>💡 מה זה אומר?</strong> עמודות ירוקות = הכנסה חודשית לכל קבוצה | עמודות כחולות = הוצאה חודשית | הפער מראה את היכולת החיסכונית של כל קבוצה
          </p>
        </div>
      </CardContent>
    </Card>
  );
};