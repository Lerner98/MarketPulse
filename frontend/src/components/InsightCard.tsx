import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface InsightCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  metric?: string;
  type?: 'success' | 'warning' | 'info' | 'error';
}

export function InsightCard({ icon: Icon, title, description, metric, type = 'info' }: InsightCardProps) {
  const typeStyles = {
    success: 'bg-success/10 border-success/20 text-success',
    warning: 'bg-warning/10 border-warning/20 text-warning',
    info: 'bg-info/10 border-info/20 text-info',
    error: 'bg-error/10 border-error/20 text-error',
  };

  return (
    <div className="bg-card rounded-lg border border-border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4" dir="rtl">
        <div className={cn('w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0', typeStyles[type])}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground mb-1">{title}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
          {metric && (
            <div className="mt-2 text-lg font-bold text-foreground">{metric}</div>
          )}
        </div>
      </div>
    </div>
  );
}
