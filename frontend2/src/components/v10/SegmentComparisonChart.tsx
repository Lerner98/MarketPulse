import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

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

export const SegmentComparisonChart = ({ data, segmentType, isLoading = false }: SegmentComparisonChartProps) => {
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

  // Transform and sort data
  const sortedData = [...data].sort((a, b) => {
    const numA = parseInt(a.segment_value.match(/\d+/)?.[0] || '0');
    const numB = parseInt(b.segment_value.match(/\d+/)?.[0] || '0');
    return numA - numB;
  });

  // Prepare Chart.js data
  const chartData = {
    labels: sortedData.map(item => translateSegmentCode(item.segment_value, segmentType)),
    datasets: [
      {
        label: 'הכנסה',
        data: sortedData.map(item => item.income),
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.2
      },
      {
        label: 'הוצאה',
        data: sortedData.map(item => item.spending),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.2
      }
    ]
  };

  // Chart.js options with RTL support
  const options = {
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
          padding: 15,
          usePointStyle: true
        }
      },
      title: {
        display: false
      },
      tooltip: {
        rtl: true,
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            label += '₪' + context.parsed.y.toLocaleString('he-IL');
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          autoSkip: false,
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 11
          }
        },
        title: {
          display: true,
          text: 'קבוצות',
          font: {
            size: 13,
            weight: 'bold' as const
          },
          padding: { top: 10 }
        }
      },
      y: {
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
          text: 'סכום (₪)',
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
          השוואת הכנסות והוצאות - {SEGMENT_DISPLAY_MAP[segmentType]?.summaryTitle || segmentType}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div style={{ height: '450px' }}>
          <Line data={chartData} options={options} />
        </div>

        {/* Explanation */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded" dir="rtl">
          <p className="text-sm text-blue-800">
            <strong>💡 מה זה אומר?</strong> קו ירוק = הכנסה חודשית | קו כחול = הוצאה חודשית | הפער ביניהם מראה כמה כל קבוצה חוסכת או מוציאה יותר מהכנסתה
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
