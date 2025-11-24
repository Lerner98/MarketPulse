import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { translateItemName } from '@/utils/translateItemName';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

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

  // Sort by inequality ratio descending, take top 8
  const sortedData = [...data]
    .sort((a, b) => b.inequality_ratio - a.inequality_ratio)
    .slice(0, 8);

  // Dynamic height based on number of items
  const chartHeight = Math.max(400, sortedData.length * 55);

  // Prepare Chart.js data - Horizontal bars
  const chartData = {
    labels: sortedData.map(item => translateItemName(item.item_name)),
    datasets: [
      {
        label: 'הוצאה גבוהה',
        data: sortedData.map(item => item.high_spend),
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1
      },
      {
        label: 'הוצאה נמוכה',
        data: sortedData.map(item => item.low_spend),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1
      }
    ]
  };

  // Chart.js options with RTL support and horizontal orientation
  const options = {
    indexAxis: 'y' as const,  // Horizontal bars
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        rtl: true,
        labels: {
          font: {
            size: 13
          },
          padding: 15
        }
      },
      title: {
        display: false
      },
      tooltip: {
        rtl: true,
        callbacks: {
          label: function(context: any) {
            const dataIndex = context.dataIndex;
            const item = sortedData[dataIndex];
            const segment = context.datasetIndex === 0 ? item.high_segment : item.low_segment;
            const value = context.parsed.x;
            return `${segment}: ₪${value.toLocaleString('he-IL')} (פער: פי ${item.inequality_ratio.toFixed(1)})`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '₪' + (value / 1000).toFixed(0) + 'K';
          },
          font: {
            size: 11
          }
        },
        title: {
          display: true,
          text: 'סכום הוצאה (₪)',
          font: {
            size: 13,
            weight: 'bold' as const
          },
          padding: { top: 10 }
        }
      },
      y: {
        ticks: {
          font: {
            size: 11
          }
        },
        title: {
          display: true,
          text: 'קטגוריות',
          font: {
            size: 13,
            weight: 'bold' as const
          },
          padding: { bottom: 10 }
        }
      }
    }
  };

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
        <div style={{ height: `${chartHeight}px` }}>
          <Bar data={chartData} options={options} />
        </div>

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
