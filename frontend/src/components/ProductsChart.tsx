import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';
import { GLOBAL_STYLES } from '@/lib/globals';
import { formatCurrency } from '@/lib/utils/hebrew';
import { ProductData } from '@/lib/types';

interface ProductsChartProps {
  data: ProductData[];
  title?: string;
}

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg shadow-lg p-3">
        <p className="font-medium text-sm mb-1" dir="rtl">{payload[0].payload.name}</p>
        <p className="text-primary font-semibold" dir="rtl">{formatCurrency(payload[0].value as number)}</p>
      </div>
    );
  }
  return null;
};

export const ProductsChart = ({ data, title = 'מוצרים מובילים לפי הכנסות' }: ProductsChartProps) => {
  const chartData = data.slice(0, 8);

  return (
    <div className={GLOBAL_STYLES.charts.container}>
      <h3 className={GLOBAL_STYLES.charts.title} dir="rtl">{title}</h3>
      <ResponsiveContainer width="100%" height={500}>
        <BarChart data={chartData} margin={{ top: 20, right: 40, left: 30, bottom: 140 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="name" 
            stroke="hsl(var(--muted-foreground))"
            angle={-45}
            textAnchor="end"
            height={120}
            interval={0}
            tick={{ fontSize: 10 }}
            dy={10}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
            width={80}
            tick={{ fontSize: 11 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="revenue" 
            fill={GLOBAL_STYLES.charts.colors.secondary}
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
