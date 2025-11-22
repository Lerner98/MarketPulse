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
            // ACTION: Filter out any segment key not found in the map (Eradication Fix)
            .filter(segment => SEGMENT_DISPLAY_MAP[segment])
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