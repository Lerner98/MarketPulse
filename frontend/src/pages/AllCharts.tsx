import { SegmentComparisonChart } from '@/components/segmentation/SegmentComparisonChart';
import { CategoryComparisonChart } from '@/components/segmentation/CategoryComparisonChart';
import { BurnRateGauge } from '@/components/segmentation/BurnRateGauge';
import { useBurnRateAnalysis } from '@/hooks/useCBSData';
import { AlertTriangle } from 'lucide-react';
import { useState, useEffect } from 'react';

const AllCharts = () => {
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  // Fetch data for multiple segments to showcase variety
  const {
    data: incomeDecileData,
    isLoading: loadingDecile
  } = useBurnRateAnalysis('Income Decile (Net)');

  const {
    data: geoData,
    isLoading: loadingGeo
  } = useBurnRateAnalysis('Geographic Region');

  const {
    data: workData,
    isLoading: loadingWork
  } = useBurnRateAnalysis('Work Status');

  const isLoading = loadingDecile || loadingGeo || loadingWork;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">
            טוען גרפים...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">
          כל הגרפים - מבט כולל על הנתונים
        </h1>
        <p className="text-muted-foreground font-medium" dir="rtl">
          צפייה מרוכזת בכל הויזואליזציות המרכזיות - מקבוצות הכנסה ועד התפלגות גיאוגרפית
        </p>
      </div>

      {/* Income Decile - Line Chart Section */}
      <div className="space-y-4">
        <div dir="rtl">
          <h2 className="text-2xl font-bold mb-1">פילוח לפי 10 דרגות הכנסה (עשירונים)</h2>
          <p className="text-sm text-muted-foreground">
            השוואה בין הכנסה להוצאה לאורך 10 קבוצות הכנסה - חושף פערים ודפוסי חיסכון
          </p>
        </div>
        <div className="w-full">
          <SegmentComparisonChart
            key={`income-decile-${windowSize.width}`}
            data={incomeDecileData?.burn_rates || []}
            segmentType="Income Decile (Net)"
            isLoading={loadingDecile}
          />
        </div>
      </div>

      {/* Geographic Region - Bar Chart Section */}
      <div className="space-y-4">
        <div dir="rtl">
          <h2 className="text-2xl font-bold mb-1">פילוח גיאוגרפי - הבדלים אזוריים</h2>
          <p className="text-sm text-muted-foreground">
            השוואת הוצאות בין אזורים שונים בישראל - מתל אביב ועד הפריפריה
          </p>
        </div>
        <div className="w-full">
          <CategoryComparisonChart
            key={`geo-region-${windowSize.width}`}
            data={geoData?.burn_rates || []}
            segmentType="Geographic Region"
            isLoading={loadingGeo}
          />
        </div>
      </div>

      {/* Work Status - Bar Chart Section */}
      <div className="space-y-4">
        <div dir="rtl">
          <h2 className="text-2xl font-bold mb-1">פילוח לפי מצב תעסוקתי</h2>
          <p className="text-sm text-muted-foreground">
            השוואה בין שכירים, עצמאיים, ולא עובדים - כיצד תעסוקה משפיעה על יציבות פיננסית
          </p>
        </div>
        <div className="w-full">
          <CategoryComparisonChart
            key={`work-status-${windowSize.width}`}
            data={workData?.burn_rates || []}
            segmentType="Work Status"
            isLoading={loadingWork}
          />
        </div>
      </div>

      {/* Income Decile - Pie Chart Section */}
      <div className="space-y-4">
        <div dir="rtl">
          <h2 className="text-2xl font-bold mb-1">התפלגות Burn Rate לפי עשירונים</h2>
          <p className="text-sm text-muted-foreground">
            ייצוג חזותי של יחס הוצאה להכנסה - מי בעודף ומי בגירעון
          </p>
        </div>
        <div className="w-full">
          <BurnRateGauge
            key={`income-gauge-${windowSize.width}`}
            data={incomeDecileData?.burn_rates || []}
            segmentType="Income Decile (Net)"
            isLoading={loadingDecile}
          />
        </div>
      </div>

      {/* Geographic Region - Pie Chart Section */}
      <div className="space-y-4">
        <div dir="rtl">
          <h2 className="text-2xl font-bold mb-1">התפלגות Burn Rate לפי אזור גיאוגרפי</h2>
          <p className="text-sm text-muted-foreground">
            מפת חום פיננסית - אילו אזורים חוסכים ואילו בלחץ כלכלי
          </p>
        </div>
        <div className="w-full">
          <BurnRateGauge
            key={`geo-gauge-${windowSize.width}`}
            data={geoData?.burn_rates || []}
            segmentType="Geographic Region"
            isLoading={loadingGeo}
          />
        </div>
      </div>

      {/* Synthesis Section - The Big Picture */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-8 mt-12" dir="rtl">
        <h2 className="text-2xl font-bold mb-4 text-purple-900">
          📈 התמונה הכוללת - מה הסיפור שמתגלה מהנתונים?
        </h2>

        <div className="space-y-6 text-gray-800">
          {/* Key Finding 1 */}
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <h3 className="text-lg font-bold mb-2 text-purple-800">
              💥 פער הכנסות קיצוני - ישראל מפוצלת כלכלית
            </h3>
            <p className="text-sm leading-relaxed">
              העשירון העליון (D10) מרוויח פי 8 מהעשירון התחתון (D1). זהו לא רק פער הכנסות - זה פער עתידות.
              בעוד D10 בונה עושר דורי (נדל"ן, מניות, עסקים), D1 נאבק על הישרדות יומיומית עם burn rate מעל 100%.
              המשמעות: שני עולמות כלכליים נפרדים לחלוטין באותה מדינה.
            </p>
          </div>

          {/* Key Finding 2 */}
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <h3 className="text-lg font-bold mb-2 text-blue-800">
              🗺️ גיאוגרפיה = גורל כלכלי
            </h3>
            <p className="text-sm leading-relaxed">
              הפער בין מרכז הארץ לפריפריה אינו רק במרחק קילומטרים - אלא בהכנסה פי 1.7 ובשיעור חיסכון של 40%.
              גוש דן והשרון מציגים הכנסות גבוהות ומשמעת פיננסית, בעוד הפריפריה מתמודדת עם הכנסות נמוכות ו-burn rate גבוה.
              המסקנה: אסטרטגיית שיווק אחת לכל הארץ = כישלון מובטח.
            </p>
          </div>

          {/* Key Finding 3 */}
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <h3 className="text-lg font-bold mb-2 text-green-800">
              💼 תעסוקה = יציבות (אבל לא תמיד)
            </h3>
            <p className="text-sm leading-relaxed">
              שכירים מציגים burn rate נמוך יחסית (77%), אך עצמאיים חיים עם burn rate של 147% - אי-יציבות כרונית.
              הסיבה: הכנסות משתנות, חוסר ביטחון תעסוקתי, וחוסר גישה למסגרות פנסיה מסודרות.
              האתגר: כיצד לספק פתרונות פיננסיים לעצמאים ששונאים סיכון אבל חיים בסיכון כלכלי מתמיד?
            </p>
          </div>

          {/* Key Finding 4 */}
          <div className="bg-white/60 rounded-lg p-4 border border-purple-100">
            <h3 className="text-lg font-bold mb-2 text-amber-800">
              🎯 עיקרון פרטו בפעולה - 30% מייצרים 60% מההוצאות
            </h3>
            <p className="text-sm leading-relaxed">
              שלושת העשירונים העליונים (D8-D10, 30% מהאוכלוסייה) אחראים ל-60%+ מכלל ההוצאות הצרכניות.
              המשמעות לעסקים: התמקדות ב-30% העליונים תניב ROI גבוה פי 2-3 מפיזור תקציב שיווק שווה על כל האוכלוסייה.
              האסטרטגיה: פילוח ממוקד - פרימיום ל-D10, value-for-money ל-D4-D7, ומחירים נמוכים ל-D1-D3.
            </p>
          </div>

          {/* Bottom Line */}
          <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-5 border-2 border-purple-300 mt-6">
            <h3 className="text-xl font-bold mb-3 text-purple-900">
              💡 המסקנה העיקרית
            </h3>
            <p className="text-sm leading-relaxed font-medium">
              ישראל אינה שוק אחד - היא <strong>3-4 שווקים שונים לחלוטין</strong> עם צרכים, כוח קנייה, ורגישות מחיר שונים.
              הצלחה עסקית דורשת <strong>פילוח מדויק ואסטרטגיה ממוקדת</strong> לכל קבוצה - לא ניתן לטפל בכולם באותו אופן.
              הנתונים של הלמ״ס 2022 מספרים סיפור ברור: <strong>הבן את הפילוח = הבן את השוק = הצלח</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Data Source Footer */}
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
            <span className="font-medium">סוגי פילוח:</span>
            <span>7 קבוצות אוכלוסייה (הכנסה, גיאוגרפיה, דמוגרפיה, תעסוקה)</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium">גרפים מרכזיים:</span>
            <span>5 ויזואליזציות מרכזיות המציגות את הסיפור הכולל</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllCharts;
