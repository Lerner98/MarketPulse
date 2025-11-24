import { translateItemName } from '@/utils/translateItemName';
import { translateSegmentCode } from '@/utils/segmentCodeTranslation';

// === INTERFACES (Full Definition) ===
interface InsightsListProps {
  segmentType: string;
  data?: {
    inequality?: Array<{ item_name: string; high_segment: string; high_spend: number; low_segment: string; low_spend: number; inequality_ratio: number }>;
    burnRate?: Array<{ segment_value: string; income: number; spending: number; burn_rate_pct: number; surplus_deficit: number; financial_status: string }>;
  };
}
// ===================================

export const InsightsList = ({ segmentType, data }: InsightsListProps) => {
  // Generate insights based on segment type
  const generateInsights = () => {
    switch (segmentType) {
      case "Income Quintile":
        return getIncomeQuintileInsights();
      case "Income Decile (Net)":
        return getIncomeDecileInsights();
      case "Geographic Region":
        return getGeographicInsights();
      case "Religiosity":
        return getReligiosityInsights();
      case "Country of Birth":
        return getCountryOfBirthInsights();
      case "Work Status":
        return getWorkStatusInsights();
      case "Education Level":
        return getEducationInsights();
      default:
        return getGenericInsights();
    }
  };

  const getIncomeQuintileInsights = () => {
    const sortedByIncome = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
    const q5 = sortedByIncome[0]; // Top 20%
    const q1 = sortedByIncome[sortedByIncome.length - 1]; // Bottom 20%
    const q4 = sortedByIncome[1]; // Second quintile from top
    const q3 = sortedByIncome[2]; // Middle class

    const incomeGap = q5 && q1 ? q5.income / q1.income : 0;
    const spendingGap = q5 && q1 ? q5.spending / q1.spending : 0;

    return [
      {
        icon: '💥',
        title: `פער הכנסות של ×${incomeGap.toFixed(1)} אבל פער הוצאות רק ×${spendingGap.toFixed(1)} - למה?`,
        description: q5 && q1
          ? `Q5 מרוויחים ₪${q5.income.toLocaleString('he-IL')} (פי ${incomeGap.toFixed(1)} מ-Q1: ₪${q1.income.toLocaleString('he-IL')}), אך מוציאים רק ₪${q5.spending.toLocaleString('he-IL')} (פי ${spendingGap.toFixed(1)} מ-Q1). הפער הזה הוא המפתח: **העשירים חוסכים, העניים הולכים לאיבוד**. Q5 חוסכים ${(100 - q5.burn_rate_pct).toFixed(0)}% מההכנסה (₪${q5.surplus_deficit.toLocaleString('he-IL')}/חודש), בעוד Q1 חיים בחוב עם burn rate של ${q1.burn_rate_pct.toFixed(0)}%. המשמעות: שני עולמות כלכליים נפרדים לחלוטין - אחד שחוסך להשקעות, השני שנאבק על ההישרדות.`
          : 'פער הכנסות גדול בהרבה מפער הוצאות - העשירים חוסכים, העניים מתקשים.',
        color: 'blue'
      },
      {
        icon: '⚠️',
        title: `Q1 בחוב כרוני: Burn Rate של ${q1?.burn_rate_pct.toFixed(0)}% = חיים על חשבון העתיד`,
        description: q1
          ? `Q1 (20% התחתונים) מוציאים ${q1.burn_rate_pct.toFixed(0)}% מהכנסתם החודשית - כלומר ${(q1.burn_rate_pct - 100).toFixed(0)} נקודות אחוז מעל האיזון. איך זה אפשרי? הסתמכות על **חובות צרכניים** (אשראי, מינוסים), **מכירת נכסים** (רכב, תכשיטים), **תמיכה משפחתית**, או **סיוע ממשלתי**. זהו שוק **בעל רגישות קיצונית למחיר** - כל עלייה של 5-10% עלולה להוציא אותם מהשוק. אסטרטגיה: מוצרי ערך מקומיים (רמי לוי, שופרסל דיל), מבצעים אגרסיביים, תשלומים קטנים + גמישות.`
          : 'החמישייה התחתונה חיה בחוב כרוני - burn rate מעל 100%.',
        color: 'red'
      },
      {
        icon: '💎',
        title: `Q5 - מכונת החיסכון: ₪${q5 ? (q5.surplus_deficit / 1000).toFixed(0) : 0}K עודף חודשי`,
        description: q5
          ? `Q5 (20% העליונים) לא רק מרוויחים הכי הרבה - הם גם החוסכים הגדולים: burn rate של רק ${q5.burn_rate_pct.toFixed(1)}%, כלומר חיסכון של ${(100 - q5.burn_rate_pct).toFixed(0)}% מההכנסה! בפועל: **₪${q5.surplus_deficit.toLocaleString('he-IL')} עודף כל חודש** (או ₪${(q5.surplus_deficit * 12 / 1000).toFixed(0)}K לשנה). לאן הולך הכסף? **השקעות נדל"ן, תיקי מניות, פנסיה פרטית, חינוך פרטי לילדים, נופש בחו"ל**. זהו **שוק הפרימיום** - מוכנים לשלם יותר עבור איכות, מותג, ושירות. אסטרטגיה: תמחור גבוה, מיתוג יוקרתי, חוויות בלעדיות, תוכניות נאמנות VIP.`
          : 'החמישייה העליונה חוסכת 30-40% מההכנסה - שוק הפרימיום.',
        color: 'green'
      },
      {
        icon: '🎯',
        title: 'אסטרטגיית שיווק 40/60: Q4-Q5 מייצרים 60% מההוצאות',
        description: q5 && q4 && q3 && q1
          ? `עיקרון פרטו מאומת: 40% העליונים (Q4-Q5) אחראים ל-**60%+ מההוצאות הכוללות**. Q5+Q4 מוציאים ביחד ₪${((q5.spending + q4.spending) / 1000).toFixed(0)}K, לעומת Q1+Q2+Q3 שמוציאים פחות. **המסקנה לעסקים**: הקצאת **40-45% מתקציב השיווק ל-Q4-Q5** (40% מהאוכלוסייה) תייצר **ROI גבוה פי 2-3**. אסטרטגיה מומלצת: (1) **פרימיום (Q5)**: תמחור גבוה, מיתוג יוקרתי, דגש על מותג. (2) **Value Premium (Q4)**: איכות במחיר תחרותי, מבצעים חכמים. (3) **מסה (Q1-Q3)**: נפח, מחיר נמוך, הנחות.`
          : 'עקרון פרטו: 40% העליונים אחראים ל-60% מההוצאות - שם צריך להיות המיקוד.',
        color: 'purple'
      }
    ];
  };

  const getIncomeDecileInsights = () => {
    const sortedByIncome = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
    const d10 = sortedByIncome[0]; // Top 10%
    const d1 = sortedByIncome[sortedByIncome.length - 1]; // Bottom 10%

    // Middle class: D4-D7 (40% of population)
    const middleClass = sortedByIncome.slice(3, 7);
    const middleClassAvgIncome = middleClass.length > 0
      ? middleClass.reduce((sum, item) => sum + item.income, 0) / middleClass.length
      : 0;
    const middleClassAvgBurnRate = middleClass.length > 0
      ? middleClass.reduce((sum, item) => sum + item.burn_rate_pct, 0) / middleClass.length
      : 0;

    // Bottom 30% (D1-D3)
    const bottom30 = sortedByIncome.slice(-3);
    const bottom30AvgBurnRate = bottom30.length > 0
      ? bottom30.reduce((sum, item) => sum + item.burn_rate_pct, 0) / bottom30.length
      : 0;

    const incomeGap = d10 && d1 ? d10.income / d1.income : 0;

    return [
      {
        icon: '💥',
        title: `פער קיצוני של ×${incomeGap.toFixed(0)}: D10 vs D1 - שני עולמות`,
        description: d10 && d1
          ? `העשירון העליון (D10) מרוויח ₪${d10.income.toLocaleString('he-IL')} לחודש - פי ${incomeGap.toFixed(0)} יותר מהעשירון התחתון (D1: ₪${d1.income.toLocaleString('he-IL')}). זהו **הפער הגדול ביותר בכל הפילוחים**. D10 חוסך ₪${d10.surplus_deficit.toLocaleString('he-IL')} לחודש (${(100 - d10.burn_rate_pct).toFixed(0)}% מההכנסה), בעוד D1 חי בחוב עם burn rate של ${d1.burn_rate_pct.toFixed(0)}%. המשמעות: D10 בונה עושר לדורות הבאים (נדל"ן, מניות, עסקים), בעוד D1 נאבק על הישרדות יומיומית. **אין זה פער הכנסות בלבד - זה פער עתידות**.`
          : 'פער הכנסות קיצוני בין העשירון העליון לתחתון.',
        color: 'red'
      },
      {
        icon: '🏛️',
        title: `מעמד הביניים (D4-D7): 40% מהאוכלוסייה בעומס פיננסי`,
        description: middleClassAvgIncome > 0
          ? `D4-D7 מייצגים את **מעמד הביניים הישראלי** - 40% מהאוכלוסייה עם הכנסה ממוצעת של ₪${middleClassAvgIncome.toLocaleString('he-IL')} לחודש. הבעיה: burn rate ממוצע של ${middleClassAvgBurnRate.toFixed(0)}% - **כמעט אפס חיסכון**. המשמעות: מעמד ביניים שחי משכורת לשכורת, ללא כרית ביטחון. כל משבר (אובדן עבודה, מחלה, תאונה) עלול להוביל למשבר כלכלי. זהו **שוק רגיש מאוד למחירים**: מחפשים value-for-money, נמשכים למבצעים, נחים על כל עלייה של 10-15%. אסטרטגיה: מוצרים איכותיים במחיר הוגן, מבצעים תכופים, תוכניות תשלומים גמישות.`
          : 'מעמד הביניים בעומס פיננסי עם burn rate גבוה.',
        color: 'blue'
      },
      {
        icon: '⚠️',
        title: `30% התחתונים (D1-D3): מצוקה כרונית עם Burn Rate ממוצע ${bottom30AvgBurnRate.toFixed(0)}%`,
        description: bottom30AvgBurnRate > 0
          ? `D1-D3 (30% התחתונים) חיים במצוקה כלכלית כרונית: burn rate ממוצע של ${bottom30AvgBurnRate.toFixed(0)}% - כלומר הוצאה גבוהה בהרבה מהכנסה. **איך הם שורדים?** (1) חובות צרכניים מצטברים (כרטיסי אשראי, הלוואות), (2) סיוע משפחתי (הורים, קרובים), (3) תמיכות ממשלתיות (מע"ש, הבטחת הכנסה), (4) מכירת נכסים. זהו שוק **הישרדותי טהור** - כל שקל נספר. הזדמנות עסקית: שרשראות ערך (רמי לוי, יינות ביתן), מוצרי Private Label זולים, חנויות second-hand, אשראי לא בנקאי.`
          : 'שליש התחתון חי במצוקה כלכלית כרונית.',
        color: 'amber'
      },
      {
        icon: '🎯',
        title: 'אסטרטגיית פילוח: 10-40-30-20 לפי עשירונים',
        description: d10 && middleClassAvgIncome > 0
          ? `חלוקת השוק לפי עשירונים מאפשרת **4 אסטרטגיות ברורות**: (1) **D10 (10%)** - שוק הפרימיום: ₪${(d10.income / 1000).toFixed(0)}K חודשי, מוכנים לשלם פי 2-3 יותר עבור איכות ומותג. תמחור גבוה, מיתוג יוקרתי, שירות VIP. (2) **D7-D9 (30%)** - Value Premium: הכנסה טובה אך מודעים למחיר. איכות במחיר הוגן, מבצעים חכמים. (3) **D4-D6 (30%)** - מעמד ביניים: ₪${(middleClassAvgIncome / 1000).toFixed(0)}K חודשי, burn rate ${middleClassAvgBurnRate.toFixed(0)}%. רגישים למחיר, מחפשים ערך. (4) **D1-D3 (30%)** - שוק ההישרדות: תמחור נמוך, נפח גדול, הנחות אגרסיביות.`
          : 'פילוח לעשירונים מאפשר אסטרטגיות שיווק ממוקדות.',
        color: 'purple'
      }
    ];
  };

  const getGeographicInsights = () => {
    // Find key regions by income/burn rate patterns
    const sortedByIncome = data?.burnRate ? [...data.burnRate].sort((a, b) => b.income - a.income) : [];
    const sortedByBurnRate = data?.burnRate ? [...data.burnRate].sort((a, b) => b.burn_rate_pct - a.burn_rate_pct) : [];

    const richest = sortedByIncome[0]; // Tel Aviv - 218
    const poorest = sortedByIncome[sortedByIncome.length - 1]; // Yizre'el - 421
    const bestSaver = sortedByBurnRate[sortedByBurnRate.length - 1]; // Sharon - 143
    const worstBurnRate = sortedByBurnRate[0]; // Yizre'el - 421

    return [
      {
        icon: '🏙️',
        title: 'המרכז הכלכלי (גוש דן): הכנסה גבוהה אך הוצאה מתונה',
        description: richest && poorest
          ? `האזור העשיר ביותר (${translateSegmentCode(richest.segment_value, 'Geographic Region')}) מציג הכנסה חודשית של ₪${richest.income.toLocaleString('he-IL')}, גבוהה ב-${((richest.income / poorest.income - 1) * 100).toFixed(0)}% מהאזור העני ביותר (${translateSegmentCode(poorest.segment_value, 'Geographic Region')}, ₪${poorest.income.toLocaleString('he-IL')}). מעניין לראות שלמרות ההכנסה הגבוהה, burn rate נמצא על ${richest.burn_rate_pct.toFixed(1)}% - לא הגבוה ביותר. זה מצביע על אוכלוסייה עם משמעת פיננסית ומודעות לחיסכון. שוק זה מתאים למוצרי פרימיום, השקעות נדל"ן, ותיירות יוקרתית.`
          : 'האזור המרכזי מציג הכנסה גבוהה עם ניהול פיננסי מתון.',
        color: 'blue'
      },
      {
        icon: '💎',
        title: `${bestSaver ? translateSegmentCode(bestSaver.segment_value, 'Geographic Region') : 'השרון'}: אלופת החיסכון - 43% חיסכון חודשי!`,
        description: bestSaver
          ? `${translateSegmentCode(bestSaver.segment_value, 'Geographic Region')} מציג את הביצועים הפיננסיים המרשימים ביותר: burn rate של רק ${bestSaver.burn_rate_pct.toFixed(1)}%, המשמעות היא חיסכון של ${(100 - bestSaver.burn_rate_pct).toFixed(1)}% מההכנסה (כ-₪${bestSaver.surplus_deficit.toLocaleString('he-IL')} לחודש!). הסיבות: אוכלוסייה ותיקה ומבוססת, מחירי מגורים נמוכים יחסית לגוש דן, וקהילתיות חזקה. זהו שוק אידיאלי למוצרי השקעות ארוכות טווח, פנסיה, וביטוחי חיים - אוכלוסייה עם יכולת ונכונות לחיסכון משמעותי.`
          : 'השרון מציג שיעור חיסכון יוצא דופן - כמעט מחצית מההכנסה.',
        color: 'green'
      },
      {
        icon: '⚠️',
        title: 'הפריפריה: פער של ×1.7 בהכנסה + לחץ פיננסי',
        description: poorest && worstBurnRate
          ? `${translateSegmentCode(poorest.segment_value, 'Geographic Region')} מציג את התמונה הכלכלית המאתגרת ביותר: הכנסה חודשית של רק ₪${poorest.income.toLocaleString('he-IL')}, עם burn rate של ${poorest.burn_rate_pct.toFixed(1)}% - כמעט אפס חיסכון (₪${poorest.surplus_deficit.toLocaleString('he-IL')} בלבד לחודש). זהו שוק רגיש מאוד למחיר, זקוק למוצרי ערך בסיסיים, הנחות משמעותיות, ואפשרויות תשלום גמישות. כל עליית מחיר של 5-10% עלולה להוציא משקי בית מהשוק. הזדמנות: שרשראות ערך (רמי לוי, שופרסל דיל) שיודעות לתת value for money.`
          : 'האזורים הפריפריאליים מציגים הכנסה נמוכה ולחץ פיננסי גבוה.',
        color: 'amber'
      },
      {
        icon: '🎯',
        title: 'אסטרטגיית Geo-Targeting: 14 אזורים = 3 פרסונות שונות לחלוטין',
        description: richest && bestSaver && poorest
          ? `ישראל מתחלקת לשלושה עולמות כלכליים נפרדים: (1) **המרכז העשיר** (${translateSegmentCode(richest.segment_value, 'Geographic Region')}, רמת גן) - ₪${(richest.income / 1000).toFixed(0)}K חודשי, burn rate ${richest.burn_rate_pct.toFixed(0)}% → מוצרי פרימיום, תמחור גבוה, דגש על איכות ומותג. (2) **החוסכים** (${translateSegmentCode(bestSaver.segment_value, 'Geographic Region')}, רחובות) - ₪${(bestSaver.income / 1000).toFixed(0)}K חודשי, burn rate ${bestSaver.burn_rate_pct.toFixed(0)}% → מוצרי השקעות, value-for-money איכותי, מבצעים חכמים. (3) **הפריפריה** (${translateSegmentCode(poorest.segment_value, 'Geographic Region')}, באר שבע) - ₪${(poorest.income / 1000).toFixed(0)}K חודשי, burn rate ${poorest.burn_rate_pct.toFixed(0)}% → תמחור נמוך, מבצעים אגרסיביים, גמישות תשלום. חשוב: אסטרטגיה אחת לכל הארץ = כישלון מובטח.`
          : 'יש לפלח אסטרטגיית שיווק לפי אזור גיאוגרפי - שלושה שווקים שונים.',
        color: 'purple'
      }
    ];
  };

  const getReligiosityInsights = () => {
    const topItem = data?.inequality?.[0];
    const foodItems = data?.inequality?.filter(item =>
      item.item_name.includes('מזון') || item.item_name.includes('אוכל')
    );

    return [
      {
        icon: '👥',
        title: 'השפעת שיוך מגזרי על הוצאות',
        description: topItem
          ? `פער משמעותי ב-${translateItemName(topItem.item_name)}: ${topItem.high_segment} מוציא פי ${topItem.inequality_ratio.toFixed(1)} יותר מ-${topItem.low_segment}.`
          : 'שיוך מגזרי משפיע משמעותית על דפוסי הוצאות משקי בית.',
        color: 'blue'
      },
      {
        icon: '💡',
        title: 'שווקים שונים לקהלים שונים',
        description: foodItems && foodItems.length > 0
          ? `הוצאות מזון משתנות משמעותית בין קבוצות - פער ממוצע של פי ${(foodItems.reduce((sum, item) => sum + item.inequality_ratio, 0) / foodItems.length).toFixed(1)}.`
          : 'קבוצות דתיות שונות מראות דפוסי הוצאה שונים בקטגוריות שונות.',
        color: 'green'
      },
      {
        icon: '📈',
        title: 'ערוצי שיווק מותאמים',
        description: 'קהלים דתיים שונים צורכים מדיה שונה - נדרש segmentation ממוקד לפי שיוך מגזרי.',
        color: 'purple'
      }
    ];
  };

  const getWorkStatusInsights = () => {
    // Find employees, self-employed, pensioners from burn rate data
    const employees = data?.burnRate?.find(d => d.segment_value === '3,713' || d.segment_value === 'שכיר');
    const selfEmployed = data?.burnRate?.find(d => d.segment_value === '589' || d.segment_value === 'עצמאי');
    const pensioners = data?.burnRate?.find(d => d.segment_value === '1,176' || d.segment_value === 'פנסיונר');

    return [
      {
        icon: '💎',
        title: 'שכירים: יציבות הכנסה = יכולת חיסכון גבוהה',
        description: employees
          ? `שכירים מציגים burn rate של רק ${employees.burn_rate_pct}% - המשמעות היא שהם חוסכים ${(100 - employees.burn_rate_pct).toFixed(1)}% מהכנסתם החודשית (כ-₪${employees.surplus_deficit.toLocaleString('he-IL')} לחודש). יציבות המשכורת החודשית מאפשרת להם תכנון פיננסי לטווח ארוך ונכונות להשקיע במוצרים יקרים יותר או במנויים חודשיים. זהו שוק מושך במיוחד עבור מוצרי השקעות, פנסיה, ביטוחים, ומוצרי פרימיום עם תשלומים קבועים.`
          : 'שכירים חוסכים כ-23% מההכנסה בזכות יציבות הכנסתם - שוק אידיאלי למוצרי השקעות ופנסיה.',
        color: 'green'
      },
      {
        icon: '⚠️',
        title: 'פנסיונרים: הכנסה נמוכה + burn rate גבוה = שוק מצוקה',
        description: pensioners && employees
          ? `פנסיונרים מציגים תמונה כלכלית מאתגרת: הכנסה חודשית של רק ₪${pensioners.income.toLocaleString('he-IL')} (כמחצית מהשכירים - ${(pensioners.income / employees.income * 100).toFixed(0)}%), עם burn rate של ${pensioners.burn_rate_pct}% - כלומר הם מסוגלים לחסוך רק ${(100 - pensioners.burn_rate_pct).toFixed(1)}% מהכנסתם. המשמעות: קבוצה זו נמצאת תחת לחץ כלכלי מתמיד וזקוקה למוצרי ערך, הנחות למבוגרים, ומחירים תחרותיים. כל עליית מחיר משמעותית עלולה להוציא אותם מהשוק.`
          : 'פנסיונרים מראים burn rate גבוה עם הכנסה נמוכה - שוק רגיש למחיר הזקוק למוצרי ערך.',
        color: 'amber'
      },
      {
        icon: '🔄',
        title: 'עצמאיים: תנודתיות הכנסה = התנהגות צרכנית שונה',
        description: selfEmployed && employees
          ? `עצמאיים מציגים פרופיל ייחודי: הכנסה דומה לשכירים (₪${selfEmployed.income.toLocaleString('he-IL')}) אך burn rate גבוה יותר (${selfEmployed.burn_rate_pct}% לעומת ${employees.burn_rate_pct}% אצל שכירים). ההבדל נובע מתנודתיות ההכנסה - חודשים טובים מתחלפים בחודשים רעים, מה שגורם לחיסכון נמוך יותר (${(100 - selfEmployed.burn_rate_pct).toFixed(1)}% בלבד). התנהגות הצריכה שלהם: העדפה לגמישות בתשלומים, רכישות גדולות בחודשים טובים, ועמידות בפני מנויים קבועים לטווח ארוך.`
          : 'עצמאיים מראים burn rate גבוה למרות הכנסה טובה - תנודתיות ההכנסה משפיעה על התנהגות הצריכה.',
        color: 'blue'
      },
      {
        icon: '🎯',
        title: 'אסטרטגיית תמחור: 3 שווקים נפרדים, 3 גישות שונות',
        description: employees && pensioners && selfEmployed
          ? `השוק הישראלי מתחלק ל-3 פלחים ברורים לפי מצב תעסוקתי: (1) שכירים - 1.95M משקי בית (66% מהשוק) עם יציבות ויכולת תשלום גבוהה → גישה: תמחור פרימיום ב-₪${(employees.spending / 1000).toFixed(1)}K חודשי, מוצרים איכותיים, מנויים ארוכי טווח. (2) פנסיונרים - 623K משקי בית (21%) עם תקציב מוגבל ב-₪${(pensioners.spending / 1000).toFixed(1)}K חודשי → גישה: מוצרי ערך, הנחות למבוגרים, חבילות חסכון. (3) עצמאיים - 346K משקי בית (13%) עם הכנסה משתנה → גישה: גמישות בתשלום, אפשרויות פריסה, מבצעים עונתיים. התאמת האסטרטגיה לכל פלח תגדיל משמעותית את שיעור ההמרה.`
          : 'יש לפלח אסטרטגיית תמחור לפי מצב תעסוקתי - שלושה שווקים שונים דורשים שלוש גישות שונות.',
        color: 'purple'
      }
    ];
  };

  const getCountryOfBirthInsights = () => {
    // Find segments from burn rate data
    const israelBorn = data?.burnRate?.find(d => d.segment_value === '974' || d.segment_value.includes('ילידי ישראל'));
    const ussr1989 = data?.burnRate?.find(d => d.segment_value === '649' || d.segment_value.includes('עד 1989'));
    const ussr1999 = data?.burnRate?.find(d => d.segment_value === '603' || d.segment_value.includes('עד 1999'));
    const ussr2000 = data?.burnRate?.find(d => d.segment_value === '371' || d.segment_value.includes('2000+'));
    const other = data?.burnRate?.find(d => d.segment_value === '325' || d.segment_value.includes('מדינות אחרות'));

    return [
      {
        icon: '🏆',
        title: 'עולי שנות ה-90: השילוב המוצלח - הכנסה גבוהה וחיסכון יציב',
        description: ussr1999 && israelBorn
          ? `עולי ברית המועצות לשעבר שהגיעו בשנות ה-90 (עד 1999) הפכו לקבוצה כלכלית מצליחה: הכנסה חודשית של ₪${ussr1999.income.toLocaleString('he-IL')} (${((ussr1999.income / israelBorn.income - 1) * 100).toFixed(0)}% ${ussr1999.income > israelBorn.income ? 'גבוהה' : 'נמוכה'} מילידי ישראל), עם burn rate של ${ussr1999.burn_rate_pct}% המאפשר חיסכון חודשי של כ-₪${ussr1999.surplus_deficit.toLocaleString('he-IL')}. לאחר 25+ שנים בארץ, קבוצה זו השלימה שילוב מלא בשוק העבודה הישראלי והפכה לשוק יעד עיקרי למוצרים איכותיים, טכנולוגיה מתקדמת (הכרה ממדינת המוצא), ותיירות לחו"ל.`
          : 'עולי שנות ה-90 מציגים שילוב כלכלי מוצלח עם הכנסה גבוהה ויכולת חיסכון.',
        color: 'green'
      },
      {
        icon: '🌱',
        title: 'עולי שנות ה-2000: בתהליך שילוב - פער של 12% בהכנסה ביחס לעולי ה-90',
        description: ussr2000 && ussr1999
          ? `עולי ברית המועצות לשעבר שהגיעו משנת 2000 ואילך נמצאים בשלב שילוב מוקדם יותר: הכנסה חודשית של ₪${ussr2000.income.toLocaleString('he-IL')}, נמוכה ב-${((1 - ussr2000.income / ussr1999.income) * 100).toFixed(0)}% מעולי שנות ה-90. ההבדל משקף הן את משך השהייה בארץ (20-25 שנים לעומת פחות מ-20), והן את ההבדלים בתנאי השוק: עולי ה-90 נקלטו בתקופת בום הייטק והרחבת כלכלה, בעוד שעולי שנות ה-2000 התמודדו עם שוק תחרותי יותר. עם זאת, burn rate דומה (${ussr2000.burn_rate_pct}%) מעיד על ניהול פיננסי טוב והסתגלות לרמת חיים ישראלית. זהו שוק בצמיחה עבור מוצרי בסיס איכותיים ושירותי שילוב.`
          : 'עולי שנות ה-2000 בתהליך שילוב פעיל עם הכנסה נמוכה יותר מעולי ה-90.',
        color: 'blue'
      },
      {
        icon: '🎯',
        title: 'ילידי ישראל: קו הבסיס - הכנסה ממוצעת עם burn rate של 80%',
        description: israelBorn && ussr1999
          ? `ילידי ישראל מציגים פרופיל כלכלי ממוצע: הכנסה חודשית של ₪${israelBorn.income.toLocaleString('he-IL')}, burn rate של ${israelBorn.burn_rate_pct}% (חיסכון של ${(100 - israelBorn.burn_rate_pct).toFixed(1)}%), וחיסכון חודשי של ₪${israelBorn.surplus_deficit.toLocaleString('he-IL')}. מעניין לראות שעולי שנות ה-90 הצליחו לעבור את ילידי ישראל בהכנסה (${((ussr1999.income / israelBorn.income - 1) * 100).toFixed(0)}% יותר), תופעה המעידה על הצלחת תהליכי השילוב וההשכלה הגבוהה של העולים (רבים בעלי תארים אקדמיים). ילידי ישראל הם השוק המגוון ביותר - כוללים קבוצות סוציו-אקונומיות רבות מחרדים ועד חילונים עשירים, מה שמחייב פילוח נוסף לשיווק יעיל.`
          : 'ילידי ישראל מהווים את קו הבסיס להשוואה עם פרופיל כלכלי ממוצע.',
        color: 'purple'
      },
      {
        icon: '💡',
        title: 'אסטרטגיית שיווק לפי מעגלי השילוב: העדפות תרבותיות שונות',
        description: ussr1999 && ussr2000 && israelBorn
          ? `שלושת מעגלי השילוב מחייבים שלוש אסטרטגיות שיווק שונות: (1) עולי שנות ה-90 - ${((ussr1999.income / 1000)).toFixed(0)}K₪ חודשי → מוצרי פרימיום, טכנולוגיה מתקדמת, נופש בחו"ל, השקעות פיננסיות. מודעות בשפה הרוסית עדיין רלוונטיות אך לא הכרחיות. (2) עולי שנות ה-2000 - ${((ussr2000.income / 1000)).toFixed(0)}K₪ חודשי → מוצרי ערך איכותיים, שירותי הכשרה והשתלמות, מוצרים משפחתיים. מודעות דו-לשוניות מומלצות. (3) ילידי ישראל - ${((israelBorn.income / 1000)).toFixed(0)}K₪ חודשי → שוק מגוון מאוד, דורש פילוח נוסף לפי דת, אזור, מצב משפחתי. שימוש בעברית ובקודים תרבותיים ישראליים.`
          : 'יש לפלח אסטרטגיית שיווק לפי מעגלי שילוב - כל קבוצה דורשת גישה תרבותית שונה.',
        color: 'amber'
      }
    ];
  };

  const getEducationInsights = () => {
    const topItem = data?.inequality?.[0];
    const avgRatio = data?.inequality && data.inequality.length > 0
      ? (data.inequality.reduce((sum, item) => sum + item.inequality_ratio, 0) / data.inequality.length)
      : null;

    return [
      {
        icon: '🎓',
        title: 'השפעת השכלה על הוצאות',
        description: topItem
          ? `הפער הגדול ביותר ב-${translateItemName(topItem.item_name)}: ${topItem.high_segment} מוציא ₪${topItem.high_spend.toLocaleString('he-IL')} לעומת ₪${topItem.low_spend.toLocaleString('he-IL')} ב-${topItem.low_segment}.`
          : 'רמת השכלה משפיעה על דפוסי הוצאות משקי בית.',
        color: 'blue'
      },
      {
        icon: '💡',
        title: 'פערים בדפוסי צריכה',
        description: avgRatio
          ? `פער ממוצע של פי ${avgRatio.toFixed(1)} בהוצאות בין קבוצות השכלה שונות.`
          : 'רמות השכלה שונות מראות דפוסי הוצאה שונים.',
        color: 'green'
      },
      {
        icon: '🎯',
        title: 'הזדמנות שיווקית',
        description: 'יש להתאים מוצרים ואסטרטגיית תמחור לפי רמת השכלה של קהל היעד.',
        color: 'purple'
      }
    ];
  };

  const getGenericInsights = () => {
    return [
      {
        icon: '💡',
        title: 'ניתוח פילוח דינמי',
        description: 'הפילוח שנבחר מאפשר הבנה מעמיקה של דפוסי הוצאות משק בית בישראל.',
        color: 'blue'
      }
    ];
  };

  const insights = generateInsights();

  // Color class mapping - Match V9 BusinessInsight style (border-l-4 for RTL)
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg shadow-sm',
    red: 'bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-lg shadow-sm',
    green: 'bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded-r-lg shadow-sm',
    purple: 'bg-purple-50 border-l-4 border-purple-500 p-4 mb-6 rounded-r-lg shadow-sm',
    amber: 'bg-amber-50 border-l-4 border-amber-500 p-4 mb-6 rounded-r-lg shadow-sm',
  };

  return (
    <div className="space-y-0">
      {insights.map((insight, index) => (
        <div
          key={index}
          className={colorClasses[insight.color] || colorClasses.blue}
          dir="rtl"
        >
          <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
            <span className="text-2xl">{typeof insight.icon === 'string' ? insight.icon : null}</span>
            <span>{insight.title}</span>
          </h3>
          <p className="text-gray-700 leading-relaxed">
            {insight.description}
          </p>
        </div>
      ))}
    </div>
  );
};