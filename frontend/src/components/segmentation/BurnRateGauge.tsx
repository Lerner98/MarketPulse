import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Gauge } from "lucide-react";
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

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

  // Filter out "Total" - pie charts show distribution, not aggregates
  const filteredData = data.filter(item =>
    item.segment_value &&
    !item.segment_value.toLowerCase().includes('total') &&
    item.segment_value !== 'Total'
  );

  // Color coding function: Red (>100%), Amber (90-100%), Green (<90%)
  const getColor = (burnRate: number) => {
    if (burnRate > 100) return "rgba(239, 68, 68, 0.8)"; // Red - overspending
    if (burnRate > 90) return "rgba(245, 158, 11, 0.8)"; // Amber - warning
    return "rgba(16, 185, 129, 0.8)"; // Green - healthy
  };

  const getBorderColor = (burnRate: number) => {
    if (burnRate > 100) return "rgba(239, 68, 68, 1)";
    if (burnRate > 90) return "rgba(245, 158, 11, 1)";
    return "rgba(16, 185, 129, 1)";
  };

  // Prepare Chart.js data (using filtered data)
  const chartData = {
    labels: filteredData.map(item => item.segment_value),
    datasets: [
      {
        label: 'יחס הוצאה',
        data: filteredData.map(item => item.burn_rate_pct),
        backgroundColor: filteredData.map(item => getColor(item.burn_rate_pct)),
        borderColor: filteredData.map(item => getBorderColor(item.burn_rate_pct)),
        borderWidth: 2
      }
    ]
  };

  // Chart.js options with RTL support
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        rtl: true,
        labels: {
          font: {
            size: 12
          },
          padding: 10,
          generateLabels: function(chart: any) {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label: string, i: number) => {
                const value = data.datasets[0].data[i];
                return {
                  text: `${label}: ${value.toFixed(1)}%`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  hidden: false,
                  index: i
                };
              });
            }
            return [];
          }
        }
      },
      tooltip: {
        rtl: true,
        callbacks: {
          label: function(context: any) {
            const dataIndex = context.dataIndex;
            const item = filteredData[dataIndex];
            const burnRate = item.burn_rate_pct;

            // Multi-line tooltip
            const lines = [
              `הכנסה: ₪${item.income.toLocaleString('he-IL')}`,
              `הוצאה: ₪${item.spending.toLocaleString('he-IL')}`,
              `יחס: ${burnRate.toFixed(1)}% מההכנסה`
            ];

            if (item.surplus_deficit >= 0) {
              lines.push(`✅ עודף: ₪${item.surplus_deficit.toLocaleString('he-IL')}`);
            } else {
              lines.push(`⚠️ גירעון: ₪${Math.abs(item.surplus_deficit).toLocaleString('he-IL')}`);
            }

            return lines;
          },
          title: function(context: any) {
            return context[0].label;
          }
        }
      }
    }
  };

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="h-5 w-5" />
          יחס הוצאה-הכנסה
        </CardTitle>
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

        <div style={{ height: '320px', position: 'relative' }}>
          <Pie data={chartData} options={options} />
        </div>

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
