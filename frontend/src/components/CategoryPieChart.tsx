import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, TooltipProps } from 'recharts';
import { GLOBAL_STYLES } from '@/lib/globals';
import { formatCurrency } from '@/lib/utils/hebrew';
import { CategoryBreakdown } from '@/lib/types';

interface CategoryPieChartProps {
  data: CategoryBreakdown[];
  title?: string;
  otherCategories?: string[];
}

const COLORS = [
  'hsl(221, 83%, 53%)',
  'hsl(262, 83%, 58%)',
  'hsl(142, 76%, 36%)',
  'hsl(45, 93%, 47%)',
  'hsl(199, 89%, 48%)',
  'hsl(280, 87%, 55%)',
  'hsl(15, 86%, 52%)',
  'hsl(160, 72%, 42%)',
];

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg shadow-lg p-3">
        <p className="font-medium text-sm mb-1" dir="rtl">{payload[0].payload.category}</p>
        <p className="text-primary font-semibold mb-1" dir="rtl">{formatCurrency(payload[0].value as number)}</p>
        <p className="text-xs text-muted-foreground" dir="rtl">{payload[0].payload.percentage.toFixed(1)}%</p>
      </div>
    );
  }
  return null;
};

export const CategoryPieChart = ({ data, title = 'חלוקה לפי קטגוריה', otherCategories }: CategoryPieChartProps) => {
  return (
    <div className={GLOBAL_STYLES.charts.container}>
      <h3 className={GLOBAL_STYLES.charts.title} dir="rtl">{title}</h3>
      <div className="bg-card border border-border rounded-lg p-6">
        <ResponsiveContainer width="100%" height={450}>
          <PieChart margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
            <Pie
              data={data}
              cx="50%"
              cy="45%"
              labelLine={false}
              label={false}
              outerRadius={130}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Custom Legend in Card */}
        <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-2">
          {data.map((entry, index) => (
            <div key={`legend-${index}`} className="flex items-center gap-1.5" dir="rtl">
              <div
                className="w-3 h-3 rounded-sm flex-shrink-0"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm">
                {entry.category} ({entry.percentage.toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>

        {/* Explanation for "Other" category */}
        {data.some(item => item.category === 'אחר') && (
          <div className="mt-4 pt-3 border-t border-border">
            <p className="text-sm text-muted-foreground text-center" dir="rtl">
              <span className="font-semibold">אחר:</span> כולל קטגוריות הוצאה משניות נוספות שלא סווגו בקטגוריות העיקריות - כגון ריהוט, טיפוח אישי, תקשורת ותחביבים
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
