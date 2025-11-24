import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';
import { GLOBAL_STYLES } from '@/lib/globals';
import { formatCurrency } from '@/lib/utils/hebrew';
import { RevenueData } from '@/lib/types';

interface RevenueChartProps {
  data: RevenueData[];
  title?: string;
}

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg shadow-lg p-3">
        <p className="font-medium text-sm mb-1" dir="rtl">{payload[0].payload.hebrewDate}</p>
        <p className="text-primary font-semibold" dir="rtl">{formatCurrency(payload[0].value as number)}</p>
      </div>
    );
  }
  return null;
};

export const RevenueChart = ({ data, title = 'מגמת הכנסות שבועית' }: RevenueChartProps) => {
  return (
    <div className={GLOBAL_STYLES.charts.container}>
      <h3 className={GLOBAL_STYLES.charts.title} dir="rtl">{title}</h3>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="dayName" 
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `₪${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="revenue" 
            stroke={GLOBAL_STYLES.charts.colors.primary}
            strokeWidth={3}
            dot={{ fill: GLOBAL_STYLES.charts.colors.primary, r: 5 }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
