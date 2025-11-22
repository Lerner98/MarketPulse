/**
 * Income Level Labels for CBS Quintile Data
 *
 * CBS divides households into 5 income groups (quintiles).
 * These labels make the data accessible to business users.
 */

export interface QuintileLabel {
  short: string;      // Short label
  full: string;       // Full descriptive label
  technical: string;  // Technical reference (Q1-Q5)
}

export const QUINTILE_LABELS: Record<number, QuintileLabel> = {
  1: {
    short: 'הכנסה נמוכה',
    full: 'משקי בית - הכנסה נמוכה',
    technical: 'Q1'
  },
  2: {
    short: 'הכנסה נמוכה-בינונית',
    full: 'משקי בית - הכנסה נמוכה-בינונית',
    technical: 'Q2'
  },
  3: {
    short: 'הכנסה בינונית',
    full: 'משקי בית - הכנסה בינונית',
    technical: 'Q3'
  },
  4: {
    short: 'הכנסה בינונית-גבוהה',
    full: 'משקי בית - הכנסה בינונית-גבוהה',
    technical: 'Q4'
  },
  5: {
    short: 'הכנסה גבוהה',
    full: 'משקי בית - הכנסה גבוהה',
    technical: 'Q5'
  }
};

/**
 * Get short label for quintile
 * @example getQuintileLabel(1) => "הכנסה נמוכה"
 */
export function getQuintileLabel(quintile: number): string {
  return QUINTILE_LABELS[quintile]?.short || `רמת הכנסה ${quintile}`;
}

/**
 * Get full descriptive label
 * @example getQuintileFullLabel(1) => "משקי בית - הכנסה נמוכה"
 */
export function getQuintileFullLabel(quintile: number): string {
  return QUINTILE_LABELS[quintile]?.full || `משקי בית - רמת הכנסה ${quintile}`;
}

/**
 * Get label with technical reference
 * @example getQuintileLabelWithRef(1) => "הכנסה נמוכה (Q1)"
 */
export function getQuintileLabelWithRef(quintile: number): string {
  const label = QUINTILE_LABELS[quintile];
  if (!label) return `רמת הכנסה ${quintile}`;
  return `${label.short} (${label.technical})`;
}
