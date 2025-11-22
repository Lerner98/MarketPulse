import { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { SegmentSelector } from '@/components/v10/SegmentSelector';
import { SegmentSummary } from '@/components/v10/SegmentSummary';
import { MetricCards } from '@/components/v10/MetricCards';
import { SegmentComparisonChart } from '@/components/v10/SegmentComparisonChart';
import { CategoryComparisonChart } from '@/components/v10/CategoryComparisonChart';
import { BurnRateGauge } from '@/components/v10/BurnRateGauge';
import { InsightsList } from '@/components/v10/InsightsList';
import { SEGMENT_DISPLAY_MAP } from '@/utils/segmentDisplayNames';
import {
  useSegmentTypes,
  useInequalityAnalysis,
  useBurnRateAnalysis,
} from '@/hooks/useCBSDataV10';

const DashboardV10 = () => {
  // Fetch available segment types
  const {
    data: segmentTypesData,
    isLoading: loadingSegmentTypes,
    error: errorSegmentTypes,
  } = useSegmentTypes();

  // State for selected segment type
  const [selectedSegmentType, setSelectedSegmentType] = useState<string>('Income Quintile');

  // Fetch inequality analysis for selected segment
  const {
    data: inequalityData,
    isLoading: loadingInequality,
    error: errorInequality,
  } = useInequalityAnalysis(selectedSegmentType, 10);

  // Fetch burn rate analysis for selected segment type
  const {
    data: burnRateData,
    isLoading: loadingBurnRate,
    error: errorBurnRate,
  } = useBurnRateAnalysis(selectedSegmentType);

  const isLoading = loadingSegmentTypes || loadingInequality || loadingBurnRate;
  const error = errorSegmentTypes || errorInequality || errorBurnRate;

  // Extract segment types from API response
  const segmentTypes = segmentTypesData?.segment_types.map(st => st.segment_type) || ['Income Quintile'];

  // Handle segment change
  const handleSegmentChange = (newSegment: string) => {
    setSelectedSegmentType(newSegment);
  };

  // Loading state
  if (loadingSegmentTypes) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">
            טוען סוגי פילוח...
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (errorSegmentTypes) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">
            שגיאה בטעינת סוגי פילוח
          </p>
          <p className="text-muted-foreground text-sm" dir="rtl">
            {errorSegmentTypes?.message || 'לא ניתן לטעון את סוגי הפילוח'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Page Header - Match V9 Style */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">
          ניתוח הוצאות משקי בית ישראליים
        </h1>
        <div className="space-y-1" dir="rtl">
          <p className="text-muted-foreground font-medium">
            ניתוח דפוסי הוצאות לפי קבוצות אוכלוסייה - נתוני הלמ״ס 2022
          </p>
          <p className="text-sm text-muted-foreground">
            מבוסס על סקר הוצאות משקי הבית של הלמ״ס (6,420 משקי בית)
          </p>
        </div>
      </div>

      {/* Segment Selector */}
      <SegmentSelector
        segments={segmentTypes}
        selectedSegment={selectedSegmentType}
        onSegmentChange={handleSegmentChange}
        isLoading={isLoading}
      />

      {/* Segment Summary */}
      <SegmentSummary segmentType={selectedSegmentType} />

      {/* Key Metrics Cards - Add Visual Variety */}
      <MetricCards
        segmentType={selectedSegmentType}
        data={{
          inequality: inequalityData?.top_inequality,
          burnRate: burnRateData?.burn_rates,
        }}
      />

      {/* Charts Section - Dynamic Chart Switching */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dynamic Chart - Line for sequential, Bar for categorical */}
        {SEGMENT_DISPLAY_MAP[selectedSegmentType]?.preferredChart === 'Line' ? (
          <SegmentComparisonChart
            data={burnRateData?.burn_rates || []}
            segmentType={selectedSegmentType}
            isLoading={loadingBurnRate}
          />
        ) : (
          <CategoryComparisonChart
            data={burnRateData?.burn_rates || []}
            segmentType={selectedSegmentType}
            isLoading={loadingBurnRate}
          />
        )}

        {/* Pie Chart - Burn Rate Distribution */}
        <BurnRateGauge
          data={burnRateData?.burn_rates || []}
          segmentType={selectedSegmentType}
          isLoading={loadingBurnRate}
        />
      </div>

      {/* Business Insights */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עסקיות ומסקנות</h2>
        <InsightsList
          segmentType={selectedSegmentType}
          data={{
            inequality: inequalityData?.top_inequality,
            burnRate: burnRateData?.burn_rates,
          }}
        />
      </div>

      {/* Data Source Info - Professional, No Technical Jargon */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-6" dir="rtl">
        <h3 className="text-lg font-semibold mb-3 text-blue-900">
          📊 אודות הנתונים
        </h3>
        <div className="space-y-2 text-sm text-gray-800">
          <div className="flex justify-between">
            <span className="font-medium">מקור:</span>
            <span>הלשכה המרכזית לסטטיסטיקה (הלמ״ס) - סקר הוצאות משקי בית 2022</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">היקף המדגם:</span>
            <span>6,420 משקי בית ישראליים</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">אפשרויות ניתוח:</span>
            <span>{segmentTypes.length} קבוצות אוכלוסייה (הכנסה, גיאוגרפיה, דמוגרפיה)</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">איכות נתונים:</span>
            <span>מעובדים ומנורמלים לניתוח מהיר ומדויק</span>
          </div>
        </div>
      </div>

      {/* Loading/Error Overlays for Data Sections */}
      {(loadingInequality || loadingBurnRate) && (
        <div className="fixed bottom-4 right-4 bg-white border border-border rounded-lg p-4 shadow-lg" dir="rtl">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span className="text-sm text-muted-foreground">טוען נתונים...</span>
          </div>
        </div>
      )}

      {(errorInequality || errorBurnRate) && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg" dir="rtl">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <span className="text-sm text-red-700">שגיאה בטעינת נתונים</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardV10;
