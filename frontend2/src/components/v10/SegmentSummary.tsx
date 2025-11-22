import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Info } from "lucide-react";
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';

interface SegmentSummaryProps {
  segmentType: string;
}

export const SegmentSummary = ({ segmentType }: SegmentSummaryProps) => {
  const summary = SEGMENT_DISPLAY_MAP[segmentType] || {
    summaryTitle: segmentType,
    summaryDescription: "ניתוח הוצאות משק בית לפי הפילוח שנבחר."
  };

  return (
    <Card className="border-blue-200 bg-blue-50/50" dir="rtl">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Info className="h-5 w-5 text-blue-600" />
          <CardTitle className="text-lg text-blue-900">{summary.summaryTitle}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-sm text-blue-800 leading-relaxed">
          {summary.summaryDescription}
        </CardDescription>
      </CardContent>
    </Card>
  );
};
