/**
 * CBS Segment Code Translation (VERIFIED)
 * Maps database codes to human-readable Hebrew labels
 *
 * SOURCE: Extracted from actual CBS Excel files on 2024-11-22
 * DO NOT modify without verifying against CBS source files
 */

// Geographic Region Codes (from CBS Table 10 - WorkStatus-IncomeSource.xlsx)
// VERIFIED: Extracted using openpyxl on 2024-11-22
// ROOT CAUSE: ETL reads header=10 which contains household sample counts as column names
// The actual region names are in rows 4-8 (multi-row header)
// Mapping: Sample count (database code) → Hebrew region name (Row 4-5)
const GEOGRAPHIC_REGION_MAP: Record<string, string> = {
  '281': 'יהודה והשומרון',  // Judea & Samaria (281 households in sample)
  '471': 'באר שבע',  // Be'er Sheva (471 households) - VERIFIED cell C6
  '405': 'אשקלון',  // Ashqelon (405 households)
  '117': 'חולון',  // Holon (117 households)
  '132': 'רמת גן',  // Ramat Gan (132 households)
  '218': 'תל אביב',  // Tel Aviv (218 households)
  '362': 'רחובות',  // Rehovot (362 households)
  '260': 'רמלה',  // Ramla (260 households)
  '230': 'פתח תקווה',  // Petah Tiqwa (230 households)
  '143': 'השרון',  // Sharon (143 households)
  '323': 'חדרה',  // Hadera (323 households)
  '551': 'חיפה',  // Haifa (551 households)
  '481': 'עכו',  // Akko (481 households)
  '421': 'יזרעאל',  // Yizre'el (421 households)
  '200': 'צפת, כנרת וגולן',  // Zefat, Kinneret & Golan (200 households)
  '883': 'ירושלים'  // Jerusalem (883 households)
};

// Work Status Codes (from CBS Table 12 - WorkStatus-IncomeSource2.xlsx)
// VERIFIED: Extracted using openpyxl on 2024-11-22
// SOURCE: Row 7-8, columns B-D
// CUSTOM: Changed "לא עובד" to "פנסיונר" (avg age 69.1 = retirees)
// Mapping: Household sample count → Hebrew employment status name
const WORK_STATUS_MAP: Record<string, string> = {
  '1,176': 'פנסיונר',      // Pensioners (1,176 households, avg age 69.1)
  '1176': 'פנסיונר',       // Same without comma
  '589': 'עצמאי',          // Self-employed (589 households)
  '3,713': 'שכיר',         // Employee (3,713 households)
  '3713': 'שכיר'           // Same without comma
};

// Education Level Codes - PLACEHOLDER (needs CBS source verification)
const EDUCATION_LEVEL_MAP: Record<string, string> = {
  // TODO: Extract from CBS source file
};

// Religiosity Codes - PLACEHOLDER (needs CBS source verification)
const RELIGIOSITY_MAP: Record<string, string> = {
  // TODO: Extract from CBS source file
};

// Country of Birth Codes (from CBS Table 11 - Household_Size.xlsx)
// VERIFIED: Cross-referenced with FILE_SPECIFICATIONS.md on 2024-11-22
// SOURCE: Column headers (Row 7-8), household sample counts
// Mapping: Household sample count → Hebrew immigration/birth status
// NOTE: Simplified labels for chart readability - focus on time period differentiation
const COUNTRY_OF_BIRTH_MAP: Record<string, string> = {
  '325': 'מדינות אחרות',       // Other countries (325 households)
  '371': "עולי ברה״מ 2000+",  // USSR immigrants 2000+ (371 households) - abbreviated
  '603': "עולי ברה״מ ה-90", // USSR immigrants 1990s (603 households) - ultra-compact
  '649': "עולי ברה״מ עד 1989", // USSR immigrants pre-1990 (649 households)
  '974': 'ילידי ישראל'          // Israel-born (974 households in sample)
};

/**
 * Translate a segment code to human-readable label
 * @param code - Raw CBS code from database
 * @param segmentType - The segment type (e.g., "Geographic Region")
 * @returns Translated Hebrew label or original code if no mapping exists
 */
export function translateSegmentCode(code: string, segmentType: string): string {
  // Check if code contains Hebrew characters (already translated)
  const hasHebrew = /[\u0590-\u05FF]/.test(code);
  if (hasHebrew) {
    return code;
  }

  switch (segmentType) {
    case 'Geographic Region':
      return GEOGRAPHIC_REGION_MAP[code] || code;
    case 'Work Status':
      return WORK_STATUS_MAP[code] || code;
    case 'Education Level':
      return EDUCATION_LEVEL_MAP[code] || code;
    case 'Religiosity':
      return RELIGIOSITY_MAP[code] || code;
    case 'Country of Birth':
      return COUNTRY_OF_BIRTH_MAP[code] || code;
    default:
      // For Income Quintile, Decile, etc. - return as-is (already formatted like "Q1", "D5")
      return code;
  }
}

/**
 * Translate segment_value in burn rate data
 * @param data - Array of burn rate items
 * @param segmentType - The segment type
 * @returns Data with translated segment_value fields
 */
export function translateBurnRateData<T extends { segment_value: string }>(
  data: T[],
  segmentType: string
): T[] {
  return data.map(item => ({
    ...item,
    segment_value: translateSegmentCode(item.segment_value, segmentType)
  }));
}
