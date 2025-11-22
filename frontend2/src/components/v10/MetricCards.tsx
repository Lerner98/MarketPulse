import { MetricCard } from './MetricCard';
import { translateItemName } from '@/utils/translateItemName';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// === INTERFACES (Full Definition) ===
interface MetricCardsProps {
  segmentType: string;
  data?: {
    inequality?: Array<{ item_name: string; high_segment: string; high_spend: number; low_segment: string; low_spend: number; inequality_ratio: number }>;
    burnRate?: Array<{ segment_value: string; income: number; spending: number; burn_rate_pct: number; surplus_deficit: number; financial_status: string }>;
  };
}
// ===================================

export const MetricCards = ({ segmentType, data }: MetricCardsProps) => {
  // Calculate metrics based on segment type
  const getMetrics = () => {
    // Work Status - Show corporate metrics (income, spending, savings, market size)
    if (segmentType === 'Work Status') {
      const avgIncome = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((sum, item) => sum + item.income, 0) / data.burnRate.length
        : 0;
      const avgSpending = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((sum, item) => sum + item.spending, 0) / data.burnRate.length
        : 0;

      // Find segment with best savings rate (lowest burn rate)
      const bestSavings = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((best, current) =>
            current.burn_rate_pct < best.burn_rate_pct ? current : best
          )
        : null;

      const savingsRate = bestSavings ? (100 - bestSavings.burn_rate_pct) : 0;

      // Total households (would need to sum from database, use placeholder for now)
      const totalHouseholds = 2921; // 623.1K + 1952K + 345.7K = 2920.8K

      return [
        {
          icon: '💰',
          value: avgIncome > 0 ? `₪${(avgIncome / 1000).toFixed(1)}K` : 'טוען...',
          label: 'הכנסה חודשית ממוצעת',
          subtitle: 'ממוצע משוקלל לכל קבוצות התעסוקה',
          color: 'blue' as const
        },
        {
          icon: '📊',
          value: avgSpending > 0 ? `₪${(avgSpending / 1000).toFixed(1)}K` : 'טוען...',
          label: 'הוצאה חודשית ממוצעת',
          subtitle: 'ממוצע משוקלל לכל קבוצות התעסוקה',
          color: 'purple' as const
        },
        {
          icon: '💎',
          value: savingsRate > 0 ? `${savingsRate.toFixed(1)}%` : 'טוען...',
          label: 'שיעור חיסכון מקסימלי',
          subtitle: bestSavings ? `שכירים: ${bestSavings.burn_rate_pct.toFixed(1)}% burn rate` : 'הקבוצה עם החיסכון הגבוה ביותר',
          color: 'green' as const
        },
        {
          icon: '👥',
          value: `${totalHouseholds}K`,
          label: 'סך משקי בית',
          subtitle: 'גודל שוק כולל לפי מצב תעסוקתי',
          color: 'amber' as const
        }
      ];
    }

    // Income Quintile - Show average metrics
    if (segmentType === 'Income Quintile') {
      const topSegment = data?.burnRate?.[data.burnRate.length - 1]; // Highest income
      const bottomSegment = data?.burnRate?.[0]; // Lowest income
      const avgIncome = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((sum, item) => sum + item.income, 0) / data.burnRate.length
        : 0;
      const avgSpending = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((sum, item) => sum + item.spending, 0) / data.burnRate.length
        : 0;
      const incomeGap = topSegment && bottomSegment
        ? topSegment.income / bottomSegment.income
        : 0;

      return [
        {
          icon: '💰',
          value: avgIncome > 0 ? `₪${(avgIncome / 1000).toFixed(0)}K` : 'טוען...',
          label: 'הכנסה חודשית ממוצעת',
          subtitle: 'ממוצע משוקלל לכל הקבוצות',
          color: 'blue' as const
        },
        {
          icon: '📊',
          value: avgSpending > 0 ? `₪${(avgSpending / 1000).toFixed(0)}K` : 'טוען...',
          label: 'הוצאה חודשית ממוצעת',
          subtitle: 'ממוצע משוקלל לכל הקבוצות',
          color: 'purple' as const
        },
        {
          icon: '📈',
          value: incomeGap > 0 ? `×${incomeGap.toFixed(1)}` : 'טוען...',
          label: 'פער הכנסות (גבוה/נמוך)',
          subtitle: topSegment && bottomSegment
            ? `${topSegment.segment_value} לעומת ${bottomSegment.segment_value}`
            : 'ההבדל בין הקבוצות',
          color: 'red' as const
        },
        {
          icon: '🎯',
          value: data?.inequality?.[0]
            ? `×${data.inequality[0].inequality_ratio.toFixed(1)}`
            : 'טוען...',
          label: 'פער הוצאות מקסימלי',
          subtitle: data?.inequality?.[0] ? translateItemName(data.inequality[0].item_name) : 'הקטגוריה עם הפער הגבוה ביותר',
          color: 'amber' as const
        }
      ];
    }

    // Income Deciles - Show different metrics (median, standard deviation, top 10% share)
    if (segmentType === 'Income Decile (Net)' || segmentType === 'Income Decile (Gross)') {
      const sortedIncome = data?.burnRate
        ? [...data.burnRate].sort((a, b) => a.income - b.income)
        : [];

      // Calculate median income (middle value)
      const medianIncome = sortedIncome.length > 0
        ? sortedIncome[Math.floor(sortedIncome.length / 2)].income
        : 0;

      // Calculate standard deviation of income
      const avgIncome = sortedIncome.length > 0
        ? sortedIncome.reduce((sum, item) => sum + item.income, 0) / sortedIncome.length
        : 0;
      const variance = sortedIncome.length > 0
        ? sortedIncome.reduce((sum, item) => sum + Math.pow(item.income - avgIncome, 2), 0) / sortedIncome.length
        : 0;
      const stdDeviation = Math.sqrt(variance);

      // Top 10% (D10) income share
      const topDecile = data?.burnRate?.[data.burnRate.length - 1];
      const topDecileShare = topDecile && avgIncome > 0
        ? (topDecile.income / avgIncome)
        : 0;

      const incomeGap = data?.burnRate && data.burnRate.length > 1
        ? data.burnRate[data.burnRate.length - 1].income / data.burnRate[0].income
        : 0;

      return [
        {
          icon: '📊',
          value: medianIncome > 0 ? `₪${(medianIncome / 1000).toFixed(0)}K` : 'טוען...',
          label: 'הכנסה חודשית חציונית',
          subtitle: 'הערך האמצעי (לא ממוצע) - עמיד יותר לקיצוניים',
          color: 'blue' as const
        },
        {
          icon: '📉',
          value: stdDeviation > 0 ? `₪${(stdDeviation / 1000).toFixed(0)}K` : 'טוען...',
          label: 'סטיית תקן של הכנסות',
          subtitle: 'מידת הפיזור - ערך גבוה = אי-שוויון גדול',
          color: 'purple' as const
        },
        {
          icon: '🏆',
          value: topDecileShare > 0 ? `×${topDecileShare.toFixed(1)}` : 'טוען...',
          label: 'יחס D10 לממוצע',
          subtitle: topDecile ? `העשירון העליון: ₪${(topDecile.income / 1000).toFixed(0)}K` : '10% העליונים',
          color: 'red' as const
        },
        {
          icon: '📈',
          value: incomeGap > 0 ? `×${incomeGap.toFixed(1)}` : 'טוען...',
          label: 'פער D10/D1',
          subtitle: 'הפער הקיצוני בין עשיר לעני',
          color: 'amber' as const
        }
      ];
    }

    // Geographic Region - Show regional economic disparity metrics
    if (segmentType === 'Geographic Region') {
      // Find key regions: Tel Aviv (218), Sharon (143), Yizre'el (421)
      const telAviv = data?.burnRate?.find(d => d.segment_value === '218' || d.segment_value.includes('תל אביב'));
      const sharon = data?.burnRate?.find(d => d.segment_value === '143' || d.segment_value.includes('השרון'));
      const yizreel = data?.burnRate?.find(d => d.segment_value === '421' || d.segment_value.includes('יזרעאל'));

      // Calculate regional income gap (highest vs lowest)
      const sortedRegions = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
      const highestIncome = sortedRegions[0];
      const lowestIncome = sortedRegions[sortedRegions.length - 1];
      const incomeGap = highestIncome && lowestIncome ? (highestIncome.income / lowestIncome.income) : 0;

      // Find region with best savings (lowest burn rate)
      const bestSavings = data?.burnRate ? [...data.burnRate].reduce((best, current) =>
        current.burn_rate_pct < best.burn_rate_pct ? current : best
      ) : null;

      // Find region with financial stress (highest burn rate)
      const worstBurnRate = data?.burnRate ? [...data.burnRate].reduce((worst, current) =>
        current.burn_rate_pct > worst.burn_rate_pct ? current : worst
      ) : null;

      return [
        {
          icon: '🏙️',
          value: highestIncome ? `₪${(highestIncome.income / 1000).toFixed(1)}K` : 'טוען...',
          label: 'הכנסה גבוהה ביותר',
          subtitle: highestIncome ? `${translateSegmentCode(highestIncome.segment_value, 'Geographic Region')} - מרכז כלכלי` : 'האזור העשיר ביותר',
          color: 'blue' as const
        },
        {
          icon: '📊',
          value: incomeGap > 0 ? `×${incomeGap.toFixed(1)}` : 'טוען...',
          label: 'פער אזורי (עשיר/עני)',
          subtitle: highestIncome && lowestIncome
            ? `${translateSegmentCode(highestIncome.segment_value, 'Geographic Region')} vs ${translateSegmentCode(lowestIncome.segment_value, 'Geographic Region')}`
            : 'פער הכנסות בין אזורים',
          color: 'amber' as const
        },
        {
          icon: '💎',
          value: bestSavings ? `${(100 - bestSavings.burn_rate_pct).toFixed(1)}%` : 'טוען...',
          label: 'שיעור חיסכון מקסימלי',
          subtitle: bestSavings ? `${translateSegmentCode(bestSavings.segment_value, 'Geographic Region')}: ${bestSavings.burn_rate_pct.toFixed(1)}% burn rate` : 'האזור החוסך ביותר',
          color: 'green' as const
        },
        {
          icon: '⚠️',
          value: worstBurnRate ? `${worstBurnRate.burn_rate_pct.toFixed(1)}%` : 'טוען...',
          label: 'Burn Rate מקסימלי',
          subtitle: worstBurnRate ? `${translateSegmentCode(worstBurnRate.segment_value, 'Geographic Region')} - לחץ פיננסי` : 'האזור עם הלחץ הכלכלי',
          color: 'red' as const
        }
      ];
    }

    // Country of Birth - Show immigration & integration metrics
    if (segmentType === 'Country of Birth') {
      const israelBorn = data?.burnRate?.find(d => d.segment_value === '974' || d.segment_value.includes('ילידי ישראל'));
      const ussr1999 = data?.burnRate?.find(d => d.segment_value === '603' || d.segment_value.includes('עד 1999'));
      const ussr2000 = data?.burnRate?.find(d => d.segment_value === '371' || d.segment_value.includes('2000+'));
      const other = data?.burnRate?.find(d => d.segment_value === '325' || d.segment_value.includes('מדינות אחרות'));

      // Integration success metric: established immigrants (1999) vs new (2000+)
      const integrationGap = ussr1999 && ussr2000
        ? ((ussr1999.income / ussr2000.income - 1) * 100)
        : 0;

      // Cultural adaptation: Israel-born vs all immigrants combined
      const avgImmigrantIncome = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.filter(d => d.segment_value !== '974').reduce((sum, item) => sum + item.income, 0) / data.burnRate.filter(d => d.segment_value !== '974').length
        : 0;

      const nativeAdvantage = israelBorn && avgImmigrantIncome > 0
        ? ((israelBorn.income / avgImmigrantIncome - 1) * 100)
        : 0;

      return [
        {
          icon: '🏠',
          value: israelBorn ? `₪${(israelBorn.income / 1000).toFixed(1)}K` : 'טוען...',
          label: 'הכנסה ילידי ישראל',
          subtitle: israelBorn ? `burn rate: ${israelBorn.burn_rate_pct.toFixed(1)}%` : 'קו הבסיס להשוואה',
          color: 'blue' as const
        },
        {
          icon: '🌍',
          value: integrationGap > 0 ? `+${integrationGap.toFixed(0)}%` : 'טוען...',
          label: 'פער שילוב (1999 לעומת 2000+)',
          subtitle: ussr1999 && ussr2000
            ? `עולי 90s: ₪${(ussr1999.income / 1000).toFixed(1)}K vs 2000s: ₪${(ussr2000.income / 1000).toFixed(1)}K`
            : 'מדד הצלחת השילוב לאורך זמן',
          color: 'green' as const
        },
        {
          icon: '📊',
          value: nativeAdvantage > 0 ? `+${nativeAdvantage.toFixed(0)}%` : nativeAdvantage < 0 ? `${nativeAdvantage.toFixed(0)}%` : 'טוען...',
          label: 'יתרון ילידים על עולים',
          subtitle: 'הפער בין ילידי ישראל לממוצע עולים',
          color: nativeAdvantage > 0 ? 'purple' as const : 'amber' as const
        },
        {
          icon: '🎯',
          value: data?.inequality?.[0]
            ? `×${data.inequality[0].inequality_ratio.toFixed(1)}`
            : 'טוען...',
          label: 'פער צריכה תרבותי מקסימלי',
          subtitle: data?.inequality?.[0] ? translateItemName(data.inequality[0].item_name) : 'הקטגוריה עם הפער הגבוה ביותר',
          color: 'red' as const
        }
      ];
    }

    // Non-income segments show inequality metrics
    const topInequality = data?.inequality?.[0];
    const avgInequality = data?.inequality && data.inequality.length > 0
      ? data.inequality.reduce((sum, item) => sum + item.inequality_ratio, 0) / data.inequality.length
      : 0;
    const totalCategories = data?.inequality?.length || 0;
    const highInequalityCount = data?.inequality?.filter(item => item.inequality_ratio > 2).length || 0;

    return [
      {
        icon: '📊',
        value: totalCategories > 0 ? `${totalCategories}` : 'טוען...',
        label: 'קטגוריות בניתוח',
        subtitle: 'סך קטגוריות הוצאה שנבדקו',
        color: 'blue' as const
      },
      {
        icon: '🎯',
        value: topInequality ? `×${topInequality.inequality_ratio.toFixed(1)}` : 'טוען...',
        label: 'פער מקסימלי',
        // ACTION: CRITICAL FIX - translateItemName applied to the subtitle here
        subtitle: topInequality ? translateItemName(topInequality.item_name) : 'הקטגוריה עם הפער הגבוה ביותר',
        color: 'red' as const
      },
      {
        icon: '📈',
        value: avgInequality > 0 ? `×${avgInequality.toFixed(1)}` : 'טוען...',
        label: 'פער ממוצע',
        subtitle: 'ממוצע הפערים בכל הקטגוריות',
        color: 'purple' as const
      },
      {
        icon: '⚠️',
        value: `${highInequalityCount}`,
        label: 'פערים גבוהים (>×2)',
        subtitle: 'קטגוריות עם פער משמעותי',
        color: 'amber' as const
      }
    ];
  };

  const metrics = getMetrics();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, index) => (
        <MetricCard key={index} {...metric} />
      ))}
    </div>
  );
};