/**
 * Translate CBS item names from English to Hebrew
 * Used across multiple components to ensure consistency
 */
export const translateItemName = (englishLabel: string): string => {
  const translations: Record<string, string> = {
    "Income tax": "מס הכנסה",
    "Pensions and social insurance funds": "מפנסיה וקרנות השתלמות",
    "From capital": "מהון",
    "Domestic help": "עזרה ביתית",
    "Insurance on dwelling and contents": "ביטוח דירה ותכולה",
    "Payments to training funds": "תשלומים לקרנות השתלמות",
    "Domestic help and cook": "עזרה ביתית ובישול",
    "Travel abroad": "נסיעות לחו״ל",
    "National insurance payments": "תשלומי ביטוח לאומי",
    "Organization dues and donations": "דמי ארגון ותרומות",
    "Compulsory payments total": "סך תשלומי חובה",
    "Compulsory payments – total": "סך תשלומי חובה",
    "Households in sample": "משקי בית במדגם",
    "Households in population (thousands)": "משקי בית באוכלוסייה (אלפים)",
    "From work": "מעבודה",
    "From self-employment and occasional work": "עצמאות ועבודות מזדמנות",
    "Other income": "הכנסות אחרות",
    "Health insurance": "ביטוח בריאות",
    "Life insurance": "ביטוח חיים",
    "Vehicle insurance": "ביטוח רכב",
    "Education": "חינוך",
    "Food and beverages": "מזון ומשקאות",
    "Housing": "דיור",
    "Transportation": "תחבורה",
    "Recreation and culture": "פנאי ותרבות",
    "Clothing and footwear": "ביגוד והנעלה",
    "Furniture and household equipment": "ריהוט וציוד לבית",
    "Communications": "תקשורת",
    "Health": "בריאות",
    "Hotels and restaurants": "בתי מלון ומסעדות",
    "Miscellaneous": "שונות"
  };
  return translations[englishLabel] || englishLabel;
};
