import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { GLOBAL_STYLES } from '@/lib/globals';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  icon: LucideIcon;
  title: string;
  value: string;
  trend?: {
    value: string;
    direction: 'up' | 'down';
  };
  iconColor?: string;
}

export const MetricCard = ({ icon: Icon, title, value, trend, iconColor = 'bg-primary/10 text-primary' }: MetricCardProps) => {
  return (
    <div className={GLOBAL_STYLES.metricCards.container}>
      <div className={cn(GLOBAL_STYLES.metricCards.icon, iconColor)}>
        <Icon className="w-6 h-6" />
      </div>
      <h3 className={GLOBAL_STYLES.metricCards.title}>{title}</h3>
      <p className={GLOBAL_STYLES.metricCards.value} dir="rtl">{value}</p>
      {trend && (
        <div className={cn(
          GLOBAL_STYLES.metricCards.trend,
          trend.direction === 'up' ? GLOBAL_STYLES.metricCards.trendUp : GLOBAL_STYLES.metricCards.trendDown
        )}>
          {trend.direction === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{trend.value}</span>
        </div>
      )}
    </div>
  );
};
