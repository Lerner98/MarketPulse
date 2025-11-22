import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";
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
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

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

export const CategoryComparisonChart = ({ data, segmentType, isLoading = false }: CategoryComparisonChartProps) => {
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

  // Determine if labels need rotation (only for Geographic Region with long names)
  const needsRotation = segmentType === 'Geographic Region';

  // Transform and sort data
  const sortedData = [...data]
    .filter(item => item && item.segment_value)
    .sort((a, b) => b.spending - a.spending);

  // Prepare Chart.js data
  const chartData = {
    labels: sortedData.map(item => translateSegmentCode(String(item.segment_value), segmentType)),
    datasets: [
      {
        label: 'הכנסה',
        data: sortedData.map(item => item.income || 0),
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1
      },
      {
        label: 'הוצאה',
        data: sortedData.map(item => item.spending || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1
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
          maxRotation: needsRotation ? 45 : 0,  // Rotate only for Geographic Region
          minRotation: needsRotation ? 45 : 0,  // Rotate only for Geographic Region
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

  // Dynamic height based on number of categories
  const chartHeight = Math.max(400, sortedData.length * 40);

  return (
    <Card dir="rtl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          השוואת הכנסות והוצאות - {SEGMENT_DISPLAY_MAP[segmentType]?.summaryTitle || segmentType}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div style={{ height: `${chartHeight}px` }}>
          <Bar data={chartData} options={options} />
        </div>

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
