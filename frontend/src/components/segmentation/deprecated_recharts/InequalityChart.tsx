import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";
import { translateItemName } from '@/utils/translateItemName';

interface InequalityData {
  item_name: string;
  high_segment: string;
  high_spend: number;
  low_segment: string;
  low_spend: number;
  inequality_ratio: number;
  avg_spend: number;
}

interface InequalityChartProps {
  data: InequalityData[];
  segmentType: string;
  isLoading?: boolean;
}

export const InequalityChart = ({ data, segmentType, isLoading = false }: InequalityChartProps) => {
  // Format numbers for Hebrew locale
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      maximumFractionDigits: 0
    }).format(value);
  };

  if (isLoading) {
    return (
      <Card dir="rtl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            טוען נתוני אי-שוויון...
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
            <TrendingUp className="h-5 w-5" />
            אי-שוויון בהוצאות
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

  // Sort by inequality ratio descending, take top 8 for readability
  const sortedData = [...data]
    .sort((a, b) => b.inequality_ratio - a.inequality_ratio)
    .slice(0, 8)
    .map(item => ({
      ...item,
      item_name_he: translateItemName(item.item_name)
    }));

  // Dynamic height based on number of items - prevents overlap
  const chartHeight = Math.max(400, sortedData.length * 55);

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Top 8 קטגוריות עם הפער הגבוה ביותר
        </CardTitle>
        <CardDescription>
          הקטגוריות שבהן יש הפער המקסימלי בהוצאות בין הקבוצות
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart
            data={sortedData}
            margin={{ top: 20, right: 30, left: 200, bottom: 20 }}
            layout="vertical"
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis
              tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
              dy={10}
            />
            <YAxis
              dataKey="item_name_he"
              width={190}
              dx={-5}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as InequalityData & { item_name_he: string };
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded shadow-lg" dir="rtl">
                      <p className="font-semibold mb-2">{data.item_name_he}</p>
                      <p className="text-sm text-green-700">
                        {data.high_segment}: {formatCurrency(data.high_spend)}
                      </p>
                      <p className="text-sm text-red-700">
                        {data.low_segment}: {formatCurrency(data.low_spend)}
                      </p>
                      <p className="text-sm text-purple-700 font-semibold mt-1">
                        פער: פי {data.inequality_ratio.toFixed(1)}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="high_spend" name="הוצאה גבוהה" fill="#10b981" />
            <Bar dataKey="low_spend" name="הוצאה נמוכה" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>

        {/* Explanation */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded" dir="rtl">
          <p className="text-sm text-blue-800">
            <strong>💡 מה זה אומר?</strong> עמודות ירוקות = קבוצה עם ההוצאה הגבוהה ביותר | עמודות אדומות = קבוצה עם ההוצאה הנמוכה ביותר | הפער ביניהן מצביע על הזדמנויות שיווקיות
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
