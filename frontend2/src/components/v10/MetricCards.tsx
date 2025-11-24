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

      // Financial discipline: Calculate burn rate range (stability indicator)
      const burnRates = data?.burnRate?.map(item => item.burn_rate_pct) || [];
      const maxBurnRate = burnRates.length > 0 ? Math.max(...burnRates) : 0;
      const minBurnRate = burnRates.length > 0 ? Math.min(...burnRates) : 0;
      const burnRateRange = maxBurnRate - minBurnRate;

      // Find worst financial control (highest burn rate)
      const worstControl = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((worst, current) =>
            current.burn_rate_pct > worst.burn_rate_pct ? current : worst
          )
        : null;

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
          subtitle: bestSavings ? `${translateSegmentCode(bestSavings.segment_value, 'Work Status')}: ${bestSavings.burn_rate_pct.toFixed(1)}% burn rate` : 'הקבוצה עם החיסכון הגבוה ביותר',
          color: 'green' as const
        },
        {
          icon: '⚖️',
          value: burnRateRange > 0 ? `${burnRateRange.toFixed(0)}%` : 'טוען...',
          label: 'פער בשליטה על הוצאות',
          subtitle: worstControl && bestSavings
            ? `${translateSegmentCode(bestSavings.segment_value, 'Work Status')} (${bestSavings.burn_rate_pct.toFixed(0)}% burn) vs ${translateSegmentCode(worstControl.segment_value, 'Work Status')} (${worstControl.burn_rate_pct.toFixed(0)}% burn)`
            : 'מי מצליח לשמור על תקציב ומי לא',
          color: 'amber' as const
        }
      ];
    }

    // Income Quintile - Show the dramatic gap story
    if (segmentType === 'Income Quintile') {
      const sortedByIncome = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
      const q5 = sortedByIncome[0]; // Top 20%
      const q1 = sortedByIncome[sortedByIncome.length - 1]; // Bottom 20%

      const incomeGap = q5 && q1 ? q5.income / q1.income : 0;
      const spendingGap = q5 && q1 ? q5.spending / q1.spending : 0;

      // Q1 burn rate to show financial stress
      const q1BurnRate = q1 ? q1.burn_rate_pct : 0;

      // Average income across all quintiles
      const avgIncome = data?.burnRate && data.burnRate.length > 0
        ? data.burnRate.reduce((sum, item) => sum + item.income, 0) / data.burnRate.length
        : 0;

      return [
        {
          icon: '⚡',
          value: incomeGap > 0 ? `×${incomeGap.toFixed(1)}` : 'טוען...',
          label: 'פער הכנסות Q5/Q1',
          subtitle: q5 && q1 ? `Q5: ₪${(q5.income / 1000).toFixed(0)}K vs Q1: ₪${(q1.income / 1000).toFixed(0)}K` : 'העשירים מרוויחים פי כמה?',
          color: 'red' as const
        },
        {
          icon: '🎯',
          value: spendingGap > 0 ? `×${spendingGap.toFixed(1)}` : 'טוען...',
          label: 'פער הוצאות Q5/Q1',
          subtitle: 'העשירים מוציאים פחות יחסית להכנסה',
          color: 'amber' as const
        },
        {
          icon: '📊',
          value: avgIncome > 0 ? `₪${(avgIncome / 1000).toFixed(1)}K` : 'טוען...',
          label: 'הכנסה ממוצעת כללית',
          subtitle: 'ממוצע כל החמישיות - ההכנסה הסטנדרטית',
          color: 'blue' as const
        },
        {
          icon: '⚠️',
          value: q1BurnRate > 0 ? `${q1BurnRate.toFixed(0)}%` : 'טוען...',
          label: 'Burn Rate של Q1',
          subtitle: q1BurnRate > 100 ? 'מעל 100% - חיים בחובות!' : 'מצוקה כלכלית',
          color: 'purple' as const
        }
      ];
    }

    // Income Deciles - Show the extreme inequality and middle-class story
    if (segmentType === 'Income Decile (Net)') {
      const sortedByIncome = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
      const d10 = sortedByIncome[0]; // Top 10%
      const d1 = sortedByIncome[sortedByIncome.length - 1]; // Bottom 10%

      const incomeGap = d10 && d1 ? d10.income / d1.income : 0;

      // Middle class (D4-D7) - 40% of population
      const middleClass = sortedByIncome.slice(3, 7); // D4, D5, D6, D7
      const middleClassAvgIncome = middleClass.length > 0
        ? middleClass.reduce((sum, item) => sum + item.income, 0) / middleClass.length
        : 0;
      const middleClassAvgBurnRate = middleClass.length > 0
        ? middleClass.reduce((sum, item) => sum + item.burn_rate_pct, 0) / middleClass.length
        : 0;

      // D1 financial stress
      const d1BurnRate = d1 ? d1.burn_rate_pct : 0;

      // Top 30% (D8-D10) - The affluent class with purchasing power
      const top30 = sortedByIncome.slice(0, 3); // D10, D9, D8
      const top30TotalSpending = top30.length > 0
        ? top30.reduce((sum, item) => sum + item.spending, 0)
        : 0;

      // Calculate what % of total spending comes from top 30%
      const totalSpending = sortedByIncome.reduce((sum, item) => sum + item.spending, 0);
      const top30SpendingShare = totalSpending > 0 ? (top30TotalSpending / totalSpending) * 100 : 0;

      return [
        {
          icon: '💥',
          value: incomeGap > 0 ? `×${incomeGap.toFixed(0)}` : 'טוען...',
          label: 'פער נטו D10/D1',
          subtitle: d10 && d1 ? `D10: ₪${(d10.income / 1000).toFixed(0)}K vs D1: ₪${(d1.income / 1000).toFixed(0)}K` : 'אי-שוויון קיצוני',
          color: 'red' as const
        },
        {
          icon: '🏛️',
          value: middleClassAvgIncome > 0 ? `₪${(middleClassAvgIncome / 1000).toFixed(0)}K` : 'טוען...',
          label: 'הכנסה ממוצעת מעמד הביניים (D4-D7)',
          subtitle: `40% מהאוכלוסייה, ${middleClassAvgBurnRate.toFixed(0)}% burn rate`,
          color: 'blue' as const
        },
        {
          icon: '💰',
          value: top30SpendingShare > 0 ? `${top30SpendingShare.toFixed(0)}%` : 'טוען...',
          label: 'נתח הוצאות של 30% העליונים',
          subtitle: `D8-D10 אחראים ל-${top30SpendingShare.toFixed(0)}% מכלל ההוצאות`,
          color: 'green' as const
        },
        {
          icon: '⚠️',
          value: d1BurnRate > 0 ? `${d1BurnRate.toFixed(0)}%` : 'טוען...',
          label: 'Burn Rate של D1',
          subtitle: d1BurnRate > 100 ? 'מצוקה קיצונית - חיים בחובות' : 'מתחת לקו העוני',
          color: 'purple' as const
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

      // Find best and worst spending discipline (burn rate)
      const sortedByBurnRate = data?.burnRate ? [...data.burnRate].sort((a, b) => a.burn_rate_pct - b.burn_rate_pct) : [];
      const bestDiscipline = sortedByBurnRate[0]; // Lowest burn rate = best savings
      const worstDiscipline = sortedByBurnRate[sortedByBurnRate.length - 1]; // Highest burn rate = worst savings
      const disciplineGap = bestDiscipline && worstDiscipline
        ? worstDiscipline.burn_rate_pct - bestDiscipline.burn_rate_pct
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
          value: disciplineGap > 0 ? `${disciplineGap.toFixed(1)}%` : 'טוען...',
          label: 'פער במשמעת פיננסית',
          subtitle: bestDiscipline && worstDiscipline
            ? `${translateSegmentCode(bestDiscipline.segment_value, 'Country of Birth')} (${bestDiscipline.burn_rate_pct.toFixed(0)}% burn) vs ${translateSegmentCode(worstDiscipline.segment_value, 'Country of Birth')} (${worstDiscipline.burn_rate_pct.toFixed(0)}% burn)`
            : 'הפער בין הקבוצה החוסכת ביותר לבזבזנית ביותר',
          color: 'purple' as const
        },
        {
          icon: '🎯',
          value: data?.inequality?.[0]
            ? `×${data.inequality[0].inequality_ratio.toFixed(1)}`
            : 'טוען...',
          label: 'פער צריכה מקסימלי',
          subtitle: data?.inequality?.[0]
            ? `${translateItemName(data.inequality[0].item_name)}: ${translateSegmentCode(data.inequality[0].high_segment, 'Country of Birth')} vs ${translateSegmentCode(data.inequality[0].low_segment, 'Country of Birth')}`
            : 'מוצר עם הפער הגבוה ביותר בין קבוצות',
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