/**
 * Single Source of Truth for all segment display names and summaries.
 * Allows quick, centralized updates to professional Hebrew terminology across the entire app.
 */

interface SegmentDisplay {
  selectorLabel: string;
  summaryTitle: string;
  summaryDescription: string;
  // Chart type hint for dynamic chart switching (Step 3)
  preferredChart: 'Line' | 'Bar';
}

export const SEGMENT_DISPLAY_MAP: Record<string, SegmentDisplay> = {
  // ----------------------------------------------------
  // Income Segments (TOP PRIORITY) - Use Line Chart for sequential data
  // ----------------------------------------------------
  "Income Decile (Net)": {
    selectorLabel: "10 דרגות הכנסה (עשירונים)",
    summaryTitle: "פילוח לפי 10 דרגות הכנסה נטו",
    summaryDescription: "עשירונים על בסיס הכנסה נטו (אחרי מיסים וביטוח לאומי) - הכסף שבפועל נשאר במשק הבית. פילוח מדויק פי-2 מחמישיות, חושף את מעמד הביניים (D4-D7) ומאפשר זיהוי מדויק של קהלי יעד צרים יותר. השוואת נתוני הברוטו חושפת את נטל המיסוי ושאלת צמצום הפערים ",
    preferredChart: 'Line',
  },
  "Income Quintile": {
    selectorLabel: "5 דרגות ההכנסה (חמישיות)",
    summaryTitle: "פילוח לפי 5 דרגות ההכנסה מהנתונים",
    summaryDescription: "חלוקה לחמישיות: מ-Q1 (20% העניים) ועד Q5 (20% העשירים). מדד הזהב לזיהוי פערים כלכליים - מראה כיצד המעמד הכלכלי קובע דפוסי צריכה, יכולת חיסכון, ואסטרטגיות שיווק ממוקדות לפי כוח קנייה.",
    preferredChart: 'Line',
  },

  // ----------------------------------------------------
  // Demographic/Categorical Segments - Use Bar Chart
  // ----------------------------------------------------
  "Geographic Region": {
    selectorLabel: "ניתוח לפי אזור גיאוגרפי",
    summaryTitle: "פילוח לפי אזור גיאוגרפי",
    summaryDescription: "השוואת הוצאות משקי בית בין אזורים שונים בישראל (ירושלים, תל אביב, חיפה, ועוד). חושף פערים אזוריים ועלויות מחיה שונות.",
    preferredChart: 'Bar',
  },
  "Work Status": {
    selectorLabel: "מצב תעסוקתי",
    summaryTitle: "פילוח לפי מצב תעסוקתי",
    summaryDescription: "ניתוח הוצאות לפי מעמד תעסוקתי (שכיר, עצמאי, לא עובד). חושף יציבות כלכלית והבדלים בדפוסי הכנסה.",
    preferredChart: 'Bar',
  },
  "Country of Birth": {
    selectorLabel: "ארץ לידה",
    summaryTitle: "פילוח לפי ארץ לידה",
    summaryDescription: "השוואת הוצאות לפי ארץ מוצא (ישראל, אירופה-אמריקה, אסיה-אפריקה, חבר העמים). משקף שוני תרבותי והשפעות הגירה.",
    preferredChart: 'Bar',
  },
  "Religiosity": {
    selectorLabel: "שיוך מגזרי",
    summaryTitle: "פילוח לפי שיוך מגזרי (קבוצות אוכלוסייה)",
    summaryDescription: "ניתוח דפוסי הוצאה לפי שיוך מגזרי (חרדי, דתי, מסורתי, חילוני). מזהה הבדלים תרבותיים בסדרי עדיפויות כלכליים.",
    preferredChart: 'Bar',
  },
  "Education Level": {
    selectorLabel: "רמת השכלה",
    summaryTitle: "פילוח לפי רמת השכלה",
    summaryDescription: "השוואת הוצאות לפי שנות לימוד (עד 12 שנה, 13-15 שנה, 16+ שנה). מראה קורלציה בין השכלה להכנסה ולדפוסי צריכה.",
    preferredChart: 'Bar',
  },
};
