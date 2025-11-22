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
      case "Income Decile (Gross)": // Combine both decile insights
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
    const topQuintile = data?.burnRate?.find(d => d?.segment_value?.includes('5'));
    const bottomQuintile = data?.burnRate?.find(d => d?.segment_value?.includes('1'));

    return [
      {
        icon: '📊',
        title: 'פער הכנסות דרמטי בין העשירים לעניים',
        description: topQuintile && bottomQuintile
          ? `משקי בית עשירים (Q5) מרוויחים ₪${topQuintile.income.toLocaleString('he-IL')} לעומת ₪${bottomQuintile.income.toLocaleString('he-IL')} למשקי בית עניים (Q1) - פער של פי ${(topQuintile.income / bottomQuintile.income).toFixed(1)}. זה לא רק סטטיסטיקה - זה מפת דרכים לאסטרטגיית שיווק מבוססת נתונים.`
          : 'משקי בית עשירים (Q5) מרוויחים פי 4-5 יותר ממשקי בית עניים (Q1), אך מוציאים רק פי 1.8-2 יותר - פער משמעותי המצביע על דפוסי צריכה שונים לחלוטין.',
        color: 'blue'
      },
      {
        icon: '⚠️',
        title: 'משקי הבית העניים (Q1) חיים מעבר ליכולתם',
        description: bottomQuintile && bottomQuintile.burn_rate_pct > 100
          ? `Q1 מוציאים ${bottomQuintile.burn_rate_pct.toFixed(1)}% מההכנסה - מעל 100%! זה אומר הסתמכות על חובות, קרנות חירום, או תמיכה משפחתית. שוק זה זקוק למוצרי ערך/בסיסיים במחיר נמוך.`
          : 'משקי בית עניים מוציאים יותר מהכנסתם (burn rate מעל 100%), מה שמעיד על מצוקה כלכלית ממשית ותלות במקורות חיצוניים.',
        color: 'red'
      },
      {
        icon: '💰',
        title: 'העשירים (Q5) חוסכים 30-40% מההכנסה',
        description: topQuintile
          ? `Q5 מראים burn rate של ${topQuintile.burn_rate_pct.toFixed(1)}%, כלומר חוסכים כ-${(100 - topQuintile.burn_rate_pct).toFixed(0)}% מההכנסה! זהו שוק פוטנציאלי ענק להשקעות, פנסיה, נדל״ן, ומוצרי פרימיום.`
          : 'משקי בית עשירים חוסכים כ-40% מההכנסה - שוק פוטנציאלי להשקעות, פנסיה, ונכסים.',
        color: 'green'
      },
      {
        icon: '🎯',
        title: 'עקרון פרטו (80/20) מאומת בנתונים',
        // ACTION: Grammar Fix: "הקצה" -> "הקצאת"
        description: '20% המשקי בית המובילים (Q4-Q5) אחראים ל-50%+ מההוצאות הכוללות. המלצה: הקצאת 40-45% מתקציב השיווק לקבוצות אלו להשגת ROI מקסימלי.',
        color: 'purple'
      }
    ];
  };

  const getIncomeDecileInsights = () => {
    return [
      {
        icon: '📈',
        title: 'פילוח מפורט יותר',
        description: 'עשירונים מאפשרים זיהוי מדויק של שכבות הביניים - D4-D7 מייצגים את "המעמד הבינוני" עם burn rate של 90-110%.',
        color: 'blue'
      },
      {
        icon: '💡',
        title: 'העשירון העליון (D10) שונה מהותית',
        description: 'D10 לא רק מרוויח יותר - יש לו דפוסי צריכה שונים (טכנולוגיה, נסיעות, חינוך פרטי) לעומת D1-D9.',
        color: 'green'
      },
      {
        icon: '⚠️',
        title: 'D1-D3 בסיכון פיננסי',
        description: '30% התחתונים מראים burn rate מעל 100%, מה שמעיד על מצוקה כלכלית ממשית.',
        color: 'amber'
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