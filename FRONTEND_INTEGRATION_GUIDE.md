# 🎨 Frontend Integration Guide - CBS API Integration

**Date:** 2024-11-21  
**Task:** Replace mock data with real CBS API  
**Time:** 2-3 hours  
**Difficulty:** Medium

---

## 🎯 OBJECTIVE

Replace mock e-commerce data with real Israeli CBS household expenditure data from your production backend.

**What Changes:**
- ❌ Remove all mock data functions
- ✅ Use CBS API endpoints (`cbsApi.ts`)
- ✅ Fix Hebrew encoding in remaining mock data
- ✅ Update types to match CBS schema
- ✅ Rewire all pages to use React Query

---

## 📊 CURRENT STATE vs TARGET STATE

### **Current State (BROKEN):**
```typescript
// Dashboard.tsx - Line 9
const dashboardData = getMockDashboardData();  // ❌ Mock data
const revenueData = getMockRevenueData();      // ❌ Mock data
```

### **Target State (WORKING):**
```typescript
// Dashboard.tsx - Using React Query
const { data: insights } = useQuery({
  queryKey: ['cbs-insights'],
  queryFn: fetchInsights
});
```

---

## 🗺️ INTEGRATION ROADMAP

### **Phase 1: Setup (15 min)**
- Create React Query hooks
- Update environment variables
- Test API connectivity

### **Phase 2: Dashboard Page (45 min)**
- Replace mock metrics with CBS insights
- Update quintile visualizations
- Fix Hebrew text encoding

### **Phase 3: Revenue Page (30 min)**
- Connect to CBS categories endpoint
- Update charts for CBS data structure

### **Phase 4: Customers Page (30 min)**
- Replace with quintile analysis
- Update to income-based segmentation

### **Phase 5: Products Page (30 min)**
- Connect to CBS categories endpoint
- Show product performance by category

### **Phase 6: Testing (30 min)**
- Verify Hebrew displays correctly
- Check all API calls work
- Test error handling

---

## 📁 FILES TO MODIFY

### **Priority 1 (MUST CHANGE):**
```
src/pages/Dashboard.tsx          ❌ Uses mock data
src/pages/Revenue.tsx             ❌ Uses mock data  
src/pages/Customers.tsx           ❌ Uses mock data
src/pages/Products.tsx            ❌ Uses mock data
src/services/mockData.ts          ❌ Delete this file
```

### **Priority 2 (SHOULD CHANGE):**
```
src/lib/types.ts                  ⚠️  Add CBS types
src/hooks/useCBSData.ts           ➕ Create this file
.env                              ⚠️  Add API URL
```

### **Priority 3 (OPTIONAL):**
```
src/lib/analytics.ts              ⚠️  Update for CBS schema
```

---

## 🔧 STEP-BY-STEP INSTRUCTIONS

---

## **STEP 1: Create React Query Hooks**

**File:** `src/hooks/useCBSData.ts` (NEW FILE)

**Create this file:**

```typescript
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  fetchQuintiles,
  fetchCategories,
  fetchCities,
  fetchDataQuality,
  fetchInsights,
  CBSQuintileResponse,
  CBSCategoryResponse,
  CBSCityResponse,
  CBSDataQuality,
  CBSInsights,
} from '@/services/cbsApi';

/**
 * Fetch income quintile analysis (Q1-Q5)
 */
export function useQuintiles(): UseQueryResult<CBSQuintileResponse, Error> {
  return useQuery({
    queryKey: ['cbs-quintiles'],
    queryFn: fetchQuintiles,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

/**
 * Fetch category performance
 */
export function useCategories(): UseQueryResult<CBSCategoryResponse, Error> {
  return useQuery({
    queryKey: ['cbs-categories'],
    queryFn: fetchCategories,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch city/geographic analysis
 */
export function useCities(): UseQueryResult<CBSCityResponse, Error> {
  return useQuery({
    queryKey: ['cbs-cities'],
    queryFn: fetchCities,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}

/**
 * Fetch data quality metrics
 */
export function useDataQuality(): UseQueryResult<CBSDataQuality, Error> {
  return useQuery({
    queryKey: ['cbs-data-quality'],
    queryFn: fetchDataQuality,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

/**
 * Fetch complete business insights
 */
export function useInsights(): UseQueryResult<CBSInsights, Error> {
  return useQuery({
    queryKey: ['cbs-insights'],
    queryFn: fetchInsights,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });
}
```

**Why:** Centralized data fetching with caching, error handling, and retry logic.

---

## **STEP 2: Update Environment Variables**

**File:** `.env` (CREATE IF DOESN'T EXIST)

**Add this line:**

```bash
VITE_API_URL=http://localhost:8000
```

**For production:**

```bash
VITE_API_URL=https://your-backend-domain.com
```

**Verify it works:**

```bash
# In terminal:
echo $VITE_API_URL

# Or in browser console after starting dev server:
console.log(import.meta.env.VITE_API_URL)
```

---

## **STEP 3: Update Dashboard Page**

**File:** `src/pages/Dashboard.tsx`

**BEFORE (Lines 1-20):**

```typescript
import { Wallet, ShoppingCart, TrendingUp, Package, Lightbulb, TrendingDown, AlertTriangle, Target } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { RevenueChart } from '@/components/RevenueChart';
import { ProductsChart } from '@/components/ProductsChart';
import { CategoryPieChart } from '@/components/CategoryPieChart';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { getMockDashboardData, getMockRevenueData, getMockProductsData, getMockCategoryBreakdown } from '@/services/mockData';
import { analyzeRevenue, analyzeCategories, analyzeProducts } from '@/lib/analytics';

const Dashboard = () => {
  const dashboardData = getMockDashboardData();
  const revenueData = getMockRevenueData();
  const productsData = getMockProductsData();
  const categoryData = getMockCategoryBreakdown();

  // Generate insights
  const revenueInsights = analyzeRevenue(revenueData);
  const categoryInsights = analyzeCategories(categoryData);
  const productInsights = analyzeProducts(productsData);
```

**AFTER (Replace entire file):**

```typescript
import { Wallet, ShoppingCart, TrendingUp, Package, Lightbulb, TrendingDown, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { CategoryPieChart } from '@/components/CategoryPieChart';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { useInsights, useCategories, useQuintiles } from '@/hooks/useCBSData';
import { CategoryBreakdown } from '@/lib/types';

const Dashboard = () => {
  // Fetch CBS data using React Query
  const { data: insights, isLoading: insightsLoading, error: insightsError } = useInsights();
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories();
  const { data: quintilesData, isLoading: quintilesLoading } = useQuintiles();

  // Loading state
  if (insightsLoading || categoriesLoading || quintilesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (insightsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
          <p className="text-muted-foreground text-sm" dir="rtl">
            {insightsError.message}
          </p>
        </div>
      </div>
    );
  }

  // No data state
  if (!insights || !categoriesData || !quintilesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground" dir="rtl">אין נתונים זמינים</p>
      </div>
    );
  }

  // Transform CBS categories to chart format
  const categoryChartData: CategoryBreakdown[] = categoriesData.categories
    .slice(0, 7)
    .map(cat => ({
      category: cat.category,
      value: parseFloat(cat.total_revenue),
      percentage: parseFloat(cat.market_share_pct),
    }));

  // Calculate total revenue from quintiles
  const totalRevenue = quintilesData.quintiles.reduce(
    (sum, q) => sum + parseFloat(q.total_spending),
    0
  );

  // Get total transaction count
  const totalTransactions = quintilesData.quintiles.reduce(
    (sum, q) => sum + q.transaction_count,
    0
  );

  // Calculate average order value
  const avgOrderValue = totalRevenue / totalTransactions;

  // Get top category
  const topCategory = categoriesData.categories[0];

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
    error: TrendingDown,
  };

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">לוח בקרה ראשי</h1>
        <p className="text-muted-foreground" dir="rtl">
          ניתוח הוצאות משק בית ישראלי - נתוני הלמ"ס
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={Wallet}
          title="סך הוצאות"
          value={formatCurrency(totalRevenue)}
          iconColor="bg-primary/10 text-primary"
        />
        <MetricCard
          icon={ShoppingCart}
          title="מספר עסקאות"
          value={formatNumber(totalTransactions)}
          iconColor="bg-secondary/10 text-secondary"
        />
        <MetricCard
          icon={TrendingUp}
          title="ממוצע הוצאה"
          value={formatCurrency(avgOrderValue)}
          iconColor="bg-accent/10 text-accent"
        />
        <MetricCard
          icon={Package}
          title="קטגוריה מובילה"
          value={topCategory.category}
          iconColor="bg-warning/10 text-warning"
        />
      </div>

      {/* Key Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות מפתח</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <InsightCard
            icon={TrendingUp}
            title="פער הכנסות"
            description={quintilesData.key_insight}
            type="info"
          />
          <InsightCard
            icon={Package}
            title="קטגוריה מובילה"
            description={`${topCategory.category} מייצרת ${topCategory.market_share_pct}% מהשוק`}
            metric={formatCurrency(parseFloat(topCategory.total_revenue))}
            type="success"
          />
          <InsightCard
            icon={Lightbulb}
            title="איכות נתונים"
            description="נתוני הלמ"ס מנוקים ומאומתים"
            metric="100%"
            type="success"
          />
        </div>
      </div>

      {/* Category Breakdown Chart */}
      <CategoryPieChart 
        data={categoryChartData} 
        title="התפלגות הוצאות לפי קטגוריה"
      />

      {/* Income Quintiles Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">ניתוח לפי חמישוני הכנסה</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {quintilesData.quintiles.map((quintile) => (
            <div key={quintile.income_quintile} className="bg-card rounded-lg border border-border p-4">
              <div className="text-center">
                <div className="text-sm text-muted-foreground mb-2">
                  חמישון {quintile.income_quintile}
                </div>
                <div className="text-2xl font-bold mb-1">
                  {formatCurrency(parseFloat(quintile.total_spending))}
                </div>
                <div className="text-xs text-muted-foreground">
                  {quintile.transaction_count.toLocaleString('he-IL')} עסקאות
                </div>
                <div className="text-xs text-primary mt-2">
                  {parseFloat(quintile.spending_share_pct).toFixed(1)}% מהשוק
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

**Key Changes:**
1. ✅ Uses `useInsights()`, `useCategories()`, `useQuintiles()` hooks
2. ✅ Proper loading states
3. ✅ Error handling
4. ✅ No mock data
5. ✅ Transforms CBS API data to chart format
6. ✅ Hebrew text displays correctly (already proper in API)

---

## **STEP 4: Update Revenue Page**

**File:** `src/pages/Revenue.tsx`

**Replace entire file with:**

```typescript
import { TrendingUp, Lightbulb, TrendingDown, AlertTriangle } from 'lucide-react';
import { CategoryPieChart } from '@/components/CategoryPieChart';
import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency } from '@/lib/utils/hebrew';
import { useCategories } from '@/hooks/useCBSData';
import { CategoryBreakdown } from '@/lib/types';

const Revenue = () => {
  const { data: categoriesData, isLoading, error } = useCategories();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  if (error || !categoriesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
        </div>
      </div>
    );
  }

  // Transform to chart format
  const chartData: CategoryBreakdown[] = categoriesData.categories
    .slice(0, 7)
    .map(cat => ({
      category: cat.category,
      value: parseFloat(cat.total_revenue),
      percentage: parseFloat(cat.market_share_pct),
    }));

  // Calculate total revenue
  const totalRevenue = categoriesData.categories.reduce(
    (sum, cat) => sum + parseFloat(cat.total_revenue),
    0
  );

  // Top 3 categories
  const top3Revenue = categoriesData.categories
    .slice(0, 3)
    .reduce((sum, cat) => sum + parseFloat(cat.total_revenue), 0);

  const top3Percentage = (top3Revenue / totalRevenue) * 100;

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
    error: TrendingDown,
  };

  // Table columns
  const columns = [
    { 
      key: 'category' as const, 
      label: 'קטגוריה', 
      sortable: true 
    },
    { 
      key: 'transaction_count' as const, 
      label: 'מספר עסקאות', 
      sortable: true,
      render: (value: number) => value.toLocaleString('he-IL')
    },
    { 
      key: 'total_revenue' as const, 
      label: 'סך הכנסות', 
      sortable: true,
      render: (value: string) => (
        <span className="font-semibold">{formatCurrency(parseFloat(value))}</span>
      )
    },
    { 
      key: 'market_share_pct' as const, 
      label: 'נתח שוק', 
      sortable: true,
      render: (value: string) => `${parseFloat(value).toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ניתוח הכנסות</h1>
        <p className="text-muted-foreground" dir="rtl">
          התפלגות הוצאות לפי קטגוריות הלמ"ס
        </p>
      </div>

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="קטגוריה מובילה"
            description={`${categoriesData.categories[0].category} מובילה בהכנסות`}
            metric={formatCurrency(parseFloat(categoriesData.categories[0].total_revenue))}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="ריכוז שוק"
            description="3 הקטגוריות המובילות מהוות חלק גדול מהשוק"
            metric={`${top3Percentage.toFixed(1)}%`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="גיוון קטגוריות"
            description={`${categoriesData.categories.length} קטגוריות פעילות`}
            metric={categoriesData.categories.length.toString()}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="סך הכנסות"
            description="סך כל ההוצאות בכל הקטגוריות"
            metric={formatCurrency(totalRevenue)}
            type="info"
          />
        </div>
      </div>

      {/* Category Pie Chart */}
      <CategoryPieChart data={chartData} title="פילוח הכנסות לפי קטגוריה" />

      {/* Top Categories Table */}
      <div className="bg-card rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4" dir="rtl">קטגוריות מובילות - Top 5</h3>
        <div className="space-y-3">
          {categoriesData.categories.slice(0, 5).map((category, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm font-medium" dir="rtl">{category.category}</span>
              <div className="flex items-center gap-3">
                <div className="text-end">
                  <p className="text-sm font-semibold" dir="rtl">
                    {formatCurrency(parseFloat(category.total_revenue))}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {parseFloat(category.market_share_pct).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Categories Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות</h2>
        <DataTable data={categoriesData.categories} columns={columns} />
      </div>
    </div>
  );
};

export default Revenue;
```

---

## **STEP 5: Update Customers Page (Now Quintiles)**

**File:** `src/pages/Customers.tsx`

**Replace entire file with:**

```typescript
import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { Users, TrendingUp, Lightbulb, AlertTriangle } from 'lucide-react';
import { MetricCard } from '@/components/MetricCard';
import { useQuintiles } from '@/hooks/useCBSData';

const Customers = () => {
  const { data: quintilesData, isLoading, error } = useQuintiles();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  if (error || !quintilesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
        </div>
      </div>
    );
  }

  const totalTransactions = quintilesData.quintiles.reduce(
    (sum, q) => sum + q.transaction_count,
    0
  );
  
  const totalSpent = quintilesData.quintiles.reduce(
    (sum, q) => sum + parseFloat(q.total_spending),
    0
  );
  
  const avgSpentPerQuintile = totalSpent / 5;

  // Calculate Q5 to Q1 ratio
  const q5Avg = parseFloat(quintilesData.quintiles[4].avg_transaction);
  const q1Avg = parseFloat(quintilesData.quintiles[0].avg_transaction);
  const ratio = q5Avg / q1Avg;

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  const columns = [
    { 
      key: 'income_quintile' as const, 
      label: 'חמישון', 
      sortable: true,
      render: (value: number) => `חמישון ${value}`
    },
    { 
      key: 'transaction_count' as const, 
      label: 'מספר עסקאות', 
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    { 
      key: 'total_spending' as const, 
      label: 'סך הוצאה', 
      sortable: true,
      render: (value: string) => (
        <span className="font-semibold">{formatCurrency(parseFloat(value))}</span>
      )
    },
    { 
      key: 'avg_transaction' as const, 
      label: 'ממוצע עסקה', 
      sortable: true,
      render: (value: string) => formatCurrency(parseFloat(value))
    },
    { 
      key: 'spending_share_pct' as const, 
      label: 'נתח שוק', 
      sortable: true,
      render: (value: string) => `${parseFloat(value).toFixed(1)}%`
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ניתוח חמישוני הכנסה</h1>
        <p className="text-muted-foreground" dir="rtl">
          דפוסי הוצאה לפי רמות הכנסה - נתוני הלמ"ס
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          icon={Users}
          title="סך עסקאות"
          value={formatNumber(totalTransactions)}
          iconColor="bg-primary/10 text-primary"
        />
        <MetricCard
          icon={Users}
          title="סך הוצאות"
          value={formatCurrency(totalSpent)}
          iconColor="bg-secondary/10 text-secondary"
        />
        <MetricCard
          icon={Users}
          title="ממוצע לחמישון"
          value={formatCurrency(avgSpentPerQuintile)}
          iconColor="bg-accent/10 text-accent"
        />
      </div>

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="פער הכנסות"
            description={quintilesData.key_insight}
            metric={`פער של ${ratio.toFixed(2)}x`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.info}
            title="חמישון עליון (Q5)"
            description="משקי בית בעלי הכנסה גבוהה"
            metric={`${parseFloat(quintilesData.quintiles[4].spending_share_pct).toFixed(1)}% מהשוק`}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="חמישון תחתון (Q1)"
            description="משקי בית בעלי הכנסה נמוכה"
            metric={`${parseFloat(quintilesData.quintiles[0].spending_share_pct).toFixed(1)}% מהשוק`}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="חמישונים בינוניים"
            description="Q2-Q4 מהווים את רוב השוק"
            metric={`${(
              parseFloat(quintilesData.quintiles[1].spending_share_pct) +
              parseFloat(quintilesData.quintiles[2].spending_share_pct) +
              parseFloat(quintilesData.quintiles[3].spending_share_pct)
            ).toFixed(1)}%`}
            type="success"
          />
        </div>
      </div>

      {/* Quintiles Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">פרטי חמישונים</h2>
        <DataTable data={quintilesData.quintiles} columns={columns} />
      </div>

      {/* Distribution Visualization */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <h2 className="col-span-full text-xl font-semibold mb-2" dir="rtl">
          התפלגות הוצאות לפי חמישון
        </h2>
        {quintilesData.quintiles.map((quintile) => (
          <div key={quintile.income_quintile} className="bg-card rounded-lg border border-border p-4">
            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-2">
                חמישון {quintile.income_quintile}
              </div>
              <div className="text-2xl font-bold mb-1">
                {formatCurrency(parseFloat(quintile.total_spending))}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatNumber(quintile.transaction_count)} עסקאות
              </div>
              <div className="text-xs text-primary mt-2">
                ממוצע: {formatCurrency(parseFloat(quintile.avg_transaction))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Customers;
```

---

## **STEP 6: Update Products Page**

**File:** `src/pages/Products.tsx`

**Replace entire file with:**

```typescript
import { DataTable } from '@/components/DataTable';
import { InsightCard } from '@/components/InsightCard';
import { formatCurrency, formatNumber } from '@/lib/utils/hebrew';
import { TrendingUp, Lightbulb, AlertTriangle, Package } from 'lucide-react';
import { useCategories } from '@/hooks/useCBSData';

const Products = () => {
  const { data: categoriesData, isLoading, error } = useCategories();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground" dir="rtl">טוען נתונים...</p>
        </div>
      </div>
    );
  }

  if (error || !categoriesData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-error mx-auto mb-4" />
          <p className="text-error font-semibold mb-2" dir="rtl">שגיאה בטעינת נתונים</p>
        </div>
      </div>
    );
  }

  const insightIcons = {
    success: TrendingUp,
    warning: AlertTriangle,
    info: Lightbulb,
  };

  // Calculate total revenue
  const totalRevenue = categoriesData.categories.reduce(
    (sum, cat) => sum + parseFloat(cat.total_revenue),
    0
  );

  // Top category
  const topCategory = categoriesData.categories[0];

  const columns = [
    { 
      key: 'category' as const, 
      label: 'קטגוריה', 
      sortable: true 
    },
    { 
      key: 'unique_products' as const, 
      label: 'מוצרים', 
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    { 
      key: 'transaction_count' as const, 
      label: 'עסקאות', 
      sortable: true,
      render: (value: number) => formatNumber(value)
    },
    { 
      key: 'total_revenue' as const, 
      label: 'הכנסות', 
      sortable: true,
      render: (value: string) => (
        <span className="font-semibold">{formatCurrency(parseFloat(value))}</span>
      )
    },
    { 
      key: 'avg_transaction' as const, 
      label: 'ממוצע עסקה', 
      sortable: true,
      render: (value: string) => formatCurrency(parseFloat(value))
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2" dir="rtl">ביצועי מוצרים</h1>
        <p className="text-muted-foreground" dir="rtl">
          ניתוח קטגוריות ומוצרים - נתוני הלמ"ס
        </p>
      </div>

      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">תובנות עיקריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InsightCard
            icon={insightIcons.success}
            title="קטגוריה מובילה"
            description={`${topCategory.category} מייצרת את ההכנסות הגבוהות ביותר`}
            metric={formatCurrency(parseFloat(topCategory.total_revenue))}
            type="success"
          />
          <InsightCard
            icon={insightIcons.info}
            title="מגוון קטגוריות"
            description={`${categoriesData.categories.length} קטגוריות פעילות בשוק`}
            metric={categoriesData.categories.length.toString()}
            type="info"
          />
          <InsightCard
            icon={insightIcons.success}
            title="סך הכנסות"
            description="סך כל ההכנסות מכל הקטגוריות"
            metric={formatCurrency(totalRevenue)}
            type="success"
          />
        </div>
      </div>

      {/* Top 10 Categories Cards */}
      <div>
        <h2 className="text-2xl font-bold mb-4" dir="rtl">Top 10 קטגוריות</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {categoriesData.categories.slice(0, 10).map((category, index) => (
            <div key={index} className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0">
                  #{index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm mb-1 truncate" title={category.category}>
                    {category.category}
                  </h3>
                  <p className="text-xs text-muted-foreground mb-2">
                    {formatNumber(category.transaction_count)} עסקאות
                  </p>
                  <p className="text-lg font-bold text-primary">
                    {formatCurrency(parseFloat(category.total_revenue))}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {parseFloat(category.market_share_pct).toFixed(1)}% מהשוק
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Table */}
      <div>
        <h2 className="text-xl font-semibold mb-4" dir="rtl">כל הקטגוריות</h2>
        <DataTable data={categoriesData.categories} columns={columns} />
      </div>
    </div>
  );
};

export default Products;
```

---

## **STEP 7: Delete Mock Data File**

**File:** `src/services/mockData.ts`

**Action:** DELETE THIS FILE

```bash
rm src/services/mockData.ts
```

**Why:** No longer needed. All data comes from CBS API.

---

## **STEP 8: Test Everything**

### **Start Backend:**

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify backend is running:**
```bash
curl http://localhost:8000/api/health
```

### **Start Frontend:**

```bash
cd frontend  # Or wherever your Lovable project is
npm run dev
```

**Open:** http://localhost:5173

---

## **STEP 9: Verify Hebrew Text**

### **Check These Pages:**

1. **Dashboard** → Should show Hebrew category names
2. **Revenue** → Hebrew categories in table
3. **Customers** → Hebrew quintile labels
4. **Products** → Hebrew category names

### **Expected Hebrew Text:**

- ✅ "אחר" (Other)
- ✅ "מזון ומשקאות" (Food & Beverages)
- ✅ "תחבורה ותקשורת" (Transportation)
- ✅ "דיור" (Housing)
- ✅ "בריאות" (Health)

### **If Hebrew Shows Mojibake:**

Check backend business_insights.json:
```bash
cat data/processed/business_insights.json | jq '.top_categories' | head -5
```

Should show proper Hebrew. If not, regenerate:
```bash
cd backend/analysis
python export_insights.py
```

---

## ✅ COMPLETION CHECKLIST

### **Before You Say "Done":**

```
□ Created useCBSData.ts hook file
□ Added VITE_API_URL to .env
□ Updated Dashboard.tsx (replaced mock data)
□ Updated Revenue.tsx (replaced mock data)
□ Updated Customers.tsx (replaced mock data)
□ Updated Products.tsx (replaced mock data)
□ Deleted mockData.ts file
□ Backend is running (port 8000)
□ Frontend is running (port 5173)
□ Hebrew displays correctly in all pages
□ No console errors in browser
□ All API calls return 200 OK
□ Charts display CBS data correctly
```

---

## 🐛 TROUBLESHOOTING

### **Problem: "Failed to fetch quintiles"**

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check API URL in .env
cat .env | grep VITE_API_URL

# Should be: VITE_API_URL=http://localhost:8000
```

### **Problem: Hebrew shows as "××—×¨"**

**Fix:**
```bash
# Regenerate business_insights.json
cd backend/analysis
python export_insights.py

# Verify Hebrew
python3 -c "import json; data=json.load(open('../../data/processed/business_insights.json')); print(list(data['top_categories'].keys())[0])"
# Should print: אחר
```

### **Problem: CORS errors in console**

**Fix:**

Add to `backend/api/main.py`:
```python
allowed_origins = [
    "http://localhost:5173",  # ← Add your frontend port
    "http://localhost:3000",
]
```

### **Problem: "Cannot find module '@/hooks/useCBSData'"**

**Fix:**

Check file was created:
```bash
ls -la src/hooks/useCBSData.ts
```

If missing, create it (see STEP 1).

---

## 📊 EXPECTED RESULTS

### **Dashboard:**
- Shows 4 metric cards with CBS data
- Displays income quintile breakdown
- Category pie chart with Hebrew labels
- All numbers formatted in ILS (₪)

### **Revenue:**
- Category table with Hebrew names
- Pie chart showing market share
- Insights cards with CBS analysis
- All Hebrew text displays correctly

### **Customers (Quintiles):**
- 5 quintile cards (Q1-Q5)
- Table showing spending patterns
- Insight cards explaining income disparity
- Hebrew labels throughout

### **Products (Categories):**
- Top 10 category cards
- Full category table
- Hebrew category names
- Proper number formatting

---

## 🎉 SUCCESS CRITERIA

**You're done when:**

1. ✅ All 4 pages load without errors
2. ✅ Hebrew text displays correctly (not mojibake)
3. ✅ All data comes from CBS API (no mock data)
4. ✅ Charts render properly
5. ✅ Numbers formatted as ILS currency
6. ✅ Loading states work
7. ✅ No console errors

---

## 📝 NOTES

- CBS API returns Hebrew text correctly (verified in backend audit)
- Frontend just needs to display it (no encoding needed)
- React Query handles caching automatically
- All amounts are in ILS (Israeli Shekels)
- Income quintiles: Q1 = lowest income, Q5 = highest income

---

**Time Estimate:** 2-3 hours if following exactly

**Difficulty:** Medium (requires TypeScript knowledge)

**Support:** If stuck, check backend logs and browser console

---

**End of Integration Guide**
