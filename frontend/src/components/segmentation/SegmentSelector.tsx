import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';

// === INTERFACES (Full Definition) ===
interface SegmentSelectorProps {
  segments: string[];
  selectedSegment: string;
  onSegmentChange: (segment: string) => void;
  isLoading?: boolean;
}
// ===================================

export const SegmentSelector = ({
  segments,
  selectedSegment,
  onSegmentChange,
  isLoading = false
}: SegmentSelectorProps) => {

  // Custom sort order: Income segments first, then rest
  const sortSegments = (a: string, b: string) => {
    const order = [
      "Income Decile (Net)",
      "Income Quintile",
      "Geographic Region",
      "Work Status",
      "Country of Birth",
      "Religiosity",
      "Education Level"
    ];

    const indexA = order.indexOf(a);
    const indexB = order.indexOf(b);

    // If both are in the order array, sort by their position
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB;
    }

    // If only A is in the array, it comes first
    if (indexA !== -1) return -1;

    // If only B is in the array, it comes first
    if (indexB !== -1) return 1;

    // If neither is in the array, sort alphabetically
    return a.localeCompare(b);
  };

  return (
    <div className="flex flex-col gap-2" dir="rtl">
      <label htmlFor="segment-selector" className="text-sm font-medium text-gray-700">
        בחר פילוח לניתוח:
      </label>
      <Select
        value={selectedSegment}
        onValueChange={onSegmentChange}
        disabled={isLoading}
      >
        <SelectTrigger
          id="segment-selector"
          className="w-full md:w-[300px] text-right"
          dir="rtl"
        >
          <SelectValue placeholder="טוען פילוחים..." />
        </SelectTrigger>
        <SelectContent dir="rtl">
          {segments
            // Filter out any segment key not found in the map
            .filter(segment => SEGMENT_DISPLAY_MAP[segment])
            // Sort by custom order
            .sort(sortSegments)
            .map((segment) => (
              <SelectItem
                key={segment}
                value={segment}
                className="text-right cursor-pointer"
              >
                {SEGMENT_DISPLAY_MAP[segment].selectorLabel}
              </SelectItem>
            ))}
        </SelectContent>
      </Select>
      {isLoading && (
        <p className="text-xs text-gray-500">טוען נתוני פילוח...</p>
      )}
    </div>
  );
};