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
  // Income Segments - Use Line Chart for sequential data
  // ----------------------------------------------------
  "Income Quintile": {
    selectorLabel: "5 דרגות ההכנסה שמוצגות",
    summaryTitle: "פילוח לפי 5 דרגות ההכנסה מהנתונים",
    summaryDescription: "ניתוח ההוצאות של משקי בית לפי רמת הכנסה, מהדרגה הנמוכה (Q1) לגבוהה (Q5). פילוח זה חושף פערים במדדי חיים ודפוסי צריכה.",
    preferredChart: 'Line',
  },
  "Income Decile (Net)": {
    selectorLabel: "10 דרגות הכנסה נטו",
    summaryTitle: "פילוח לפי 10 דרגות הכנסה נטו",
    summaryDescription: "פילוח מפורט יותר של משקי בית לעשרה קבוצות לפי הכנסה נטו. מאפשר זיהוי מדויק יותר של שכבות הביניים בחברה.",
    preferredChart: 'Line',
  },
  "Income Decile (Gross)": {
    selectorLabel: "10 דרגות הכנסה ברוטו",
    summaryTitle: "פילוח לפי 10 דרגות הכנסה ברוטו",
    summaryDescription: "פילוח מפורט של משקי בית לעשרה קבוצות לפי הכנסה ברוטו (לפני מיסים). מאפשר ניתוח השפעת מיסוי על שכבות שונות.",
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
  "Religiosity": {
    selectorLabel: "שיוך מגזרי",
    summaryTitle: "פילוח לפי שיוך מגזרי (קבוצות אוכלוסייה)",
    summaryDescription: "ניתוח דפוסי הוצאה לפי שיוך מגזרי (חרדי, דתי, מסורתי, חילוני). מזהה הבדלים תרבותיים בסדרי עדיפויות כלכליים.",
    preferredChart: 'Bar',
  },
  "Country of Birth": {
    selectorLabel: "ארץ לידה",
    summaryTitle: "פילוח לפי ארץ לידה",
    summaryDescription: "השוואת הוצאות לפי ארץ מוצא (ישראל, אירופה-אמריקה, אסיה-אפריקה, חבר העמים). משקף שוני תרבותי והשפעות הגירה.",
    preferredChart: 'Bar',
  },
  "Work Status": {
    selectorLabel: "מצב תעסוקתי",
    summaryTitle: "פילוח לפי מצב תעסוקתי",
    summaryDescription: "ניתוח הוצאות לפי מעמד תעסוקתי (שכיר, עצמאי, לא עובד). חושף יציבות כלכלית והבדלים בדפוסי הכנסה.",
    preferredChart: 'Bar',
  },
  "Education Level": {
    selectorLabel: "רמת השכלה",
    summaryTitle: "פילוח לפי רמת השכלה",
    summaryDescription: "השוואת הוצאות לפי שנות לימוד (עד 12 שנה, 13-15 שנה, 16+ שנה). מראה קורלציה בין השכלה להכנסה ולדפוסי צריכה.",
    preferredChart: 'Bar',
  },
};
