interface BusinessInsightProps {
  title: string;
  insight: string;
  action: string;
  color?: 'blue' | 'green' | 'purple' | 'yellow';
  icon?: string;
}

export function BusinessInsight({
  title,
  insight,
  action,
  color = 'blue',
  icon = '💡'
}: BusinessInsightProps) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-500',
      text: 'text-blue-600'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-500',
      text: 'text-green-600'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-500',
      text: 'text-purple-600'
    },
    yellow: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-500',
      text: 'text-yellow-600'
    }
  };

  const colors = colorMap[color];

  return (
    <div className={`${colors.bg} border-l-4 ${colors.border} p-4 mb-6 rounded-r-lg shadow-sm`} dir="rtl">
      <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
        <span className="text-2xl">{icon}</span>
        <span>{title}</span>
      </h3>
      <p className="text-gray-700 leading-relaxed">
        <strong>{insight}</strong>{' '}
        <span className={`${colors.text} font-semibold`}>{action}</span>
      </p>
    </div>
  );
}
