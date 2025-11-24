import { Card, CardContent } from "@/components/ui/card";

interface MetricCardProps {
  icon: string;
  value: string;
  label: string;
  subtitle?: string;
  color: 'blue' | 'green' | 'red' | 'purple' | 'amber';
}

const colorClasses: Record<string, { bg: string; text: string; icon: string }> = {
  blue: { bg: 'bg-blue-50', text: 'text-blue-700', icon: 'bg-blue-100' },
  green: { bg: 'bg-green-50', text: 'text-green-700', icon: 'bg-green-100' },
  red: { bg: 'bg-red-50', text: 'text-red-700', icon: 'bg-red-100' },
  purple: { bg: 'bg-purple-50', text: 'text-purple-700', icon: 'bg-purple-100' },
  amber: { bg: 'bg-amber-50', text: 'text-amber-700', icon: 'bg-amber-100' },
};

export const MetricCard = ({ icon, value, label, subtitle, color }: MetricCardProps) => {
  const colors = colorClasses[color];

  return (
    <Card className={`${colors.bg} border-2 border-${color}-200`} dir="rtl">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm text-gray-600 font-medium mb-1">{label}</p>
            <h3 className={`text-3xl font-bold ${colors.text}`}>{value}</h3>
            {subtitle && (
              <p className="text-xs text-gray-600 mt-2">{subtitle}</p>
            )}
          </div>
          <div className={`text-4xl ${colors.icon} p-4 rounded-full flex-shrink-0`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
