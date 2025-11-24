# Archived Frontend Code - V9 to V10 Migration

**Archive Date:** November 22, 2025
**Migration:** MarketPulse V9 → V10 (Phase 5 Frontend)

---

## Why These Files Were Archived

V10 introduced a **normalized star schema** and **dynamic segment selection** that made V9's hardcoded, segment-specific pages obsolete.

**Key V10 Changes:**
- ✅ Single dynamic dashboard (replaces 3 separate pages)
- ✅ 7 segment types supported (not just 3)
- ✅ Star schema backend (dim_segment + fact_expenditure)
- ✅ React Query for data fetching
- ✅ Component-driven architecture

---

## Directory Structure

```
archive/
├── v9-pages/                    # Old dashboard pages
│   ├── Dashboard.tsx            # Original V9 dashboard (3 insights)
│   ├── DashboardV9.tsx          # V9 backup
│   └── Dashboard.tsx.bak        # Backup file
│
├── v9-services/                 # Old API clients
│   ├── cbsApi.ts                # Original V9 API client
│   └── cbsApiV9.ts              # V9 backup
│
├── v9-hooks/                    # Old React hooks
│   ├── useCBSData.ts            # Original V9 hooks
│   └── useCBSDataV9.ts          # V9 backup
│
├── deprecated-synthetic-pages/  # Obsolete synthetic data pages
│   ├── Customers.tsx            # Synthetic customer analysis
│   ├── Products.tsx             # Synthetic product performance
│   └── Revenue.tsx              # Synthetic revenue breakdown
│
└── README.md                    # This file
```

---

## What Was Archived

### 1. V9 Pages (v9-pages/)

**Dashboard.tsx** - Original V9 dashboard
- **What it did:** Displayed 3 hardcoded business insights (Quintile Gap, Category Distribution, Pareto)
- **Why archived:** V10 has 5 dynamic insights that generate based on selected segment type
- **Line count:** ~300 lines
- **Key limitation:** Hardcoded to Income Quintile only

**DashboardV9.tsx** - V9 backup
- **What it did:** Backup copy of V9 dashboard
- **Why archived:** Duplicate of Dashboard.tsx

**Dashboard.tsx.bak** - Old backup file
- **What it did:** Backup from earlier development
- **Why archived:** No longer needed

---

### 2. V9 Services (v9-services/)

**cbsApi.ts** - Original V9 API client
- **What it did:** Fetched data from 3 hardcoded V9 endpoints:
  - `/api/cbs/quintiles`
  - `/api/cbs/categories`
  - `/api/cbs/insights`
- **Why archived:** V10 uses dynamic endpoints:
  - `/api/v10/segments/types` (get all segment types)
  - `/api/v10/burn-rate?segment_type={type}`
  - `/api/v10/inequality/{type}`
- **Replacement:** `cbsApiV10.ts` (still in `src/services/`)

**cbsApiV9.ts** - V9 backup
- **What it did:** Backup copy of cbsApi.ts
- **Why archived:** Duplicate

---

### 3. V9 Hooks (v9-hooks/)

**useCBSData.ts** - Original V9 React hooks
- **What it did:** React Query hooks for V9 endpoints:
  - `useQuintiles()` - Fetch quintile data
  - `useCategories()` - Fetch category breakdown
  - `useInsights()` - Fetch hardcoded insights
- **Why archived:** V10 uses dynamic hooks:
  - `useSegmentTypes()` - Fetch all segment types
  - `useBurnRateAnalysis(segmentType)` - Dynamic burn rate
  - `useInequalityAnalysis(segmentType, topN)` - Dynamic inequality
- **Replacement:** `useCBSDataV10.ts` (still in `src/hooks/`)

**useCBSDataV9.ts** - V9 backup
- **What it did:** Backup copy of useCBSData.ts
- **Why archived:** Duplicate

---

### 4. Deprecated Synthetic Pages (deprecated-synthetic-pages/)

**Customers.tsx** - Synthetic customer segmentation
- **What it did:** Displayed fake customer data (not real CBS data)
- **Why deprecated:** Project pivoted to 100% real CBS data
- **Line count:** ~350 lines
- **Status:** Never used in production

**Products.tsx** - Synthetic product performance
- **What it did:** Displayed fake product sales data
- **Why deprecated:** Not aligned with CBS household expenditure focus
- **Line count:** ~300 lines
- **Status:** Never used in production

**Revenue.tsx** - Synthetic revenue breakdown
- **What it did:** Displayed fake revenue charts
- **Why deprecated:** CBS data doesn't include revenue (only household spending)
- **Line count:** ~350 lines
- **Status:** Never used in production

---

## V9 vs V10: Key Differences

| Aspect | V9 (Archived) | V10 (Current) |
|--------|---------------|---------------|
| **Pages** | 3 separate pages (Dashboard, Customers, Products) | 1 dynamic page (DashboardV10) |
| **Insights** | 3 hardcoded insights | 5 dynamic insights (segment-aware) |
| **Segment Types** | 1 type (Income Quintile only) | 7 types (Quintile, Decile, Region, etc.) |
| **API Endpoints** | 3 fixed endpoints | 4 dynamic endpoints with parameters |
| **Data Source** | Mix of real CBS + synthetic | 100% real CBS data (6,420 records) |
| **Scalability** | Hardcoded (add segment = rewrite pages) | Dynamic (add segment = update config) |
| **Code Lines** | ~1,200 lines across 6 files | ~800 lines across 6 files |

---

## Migration Timeline

| Date | Action |
|------|--------|
| **Nov 20, 2025** | V9 backend complete (3 CBS files) |
| **Nov 21, 2025** | V10 backend complete (7 CBS files, star schema) |
| **Nov 22, 2025** | Phase 5: V9 frontend archived, V10 frontend implemented |

---

## Can I Restore V9 Code?

**Yes, but you shouldn't.**

V9 code is preserved here for:
- ✅ Historical reference
- ✅ Understanding architecture evolution
- ✅ Learning from past decisions

**Don't restore V9 because:**
- ❌ V10 backend no longer supports V9 endpoints
- ❌ Hardcoded design doesn't scale
- ❌ Missing 4 segment types
- ❌ Portfolio requires V10 for "dynamic segmentation" showcase

---

## V10 Active Files

**Current production files (NOT archived):**

```
src/
├── pages/
│   ├── DashboardV10.tsx         ← Main dashboard (rewritten for V10)
│   └── NotFound.tsx             ← 404 page
│
├── components/
│   └── v10/                     ← NEW: V10 dynamic components
│       ├── SegmentSelector.tsx
│       ├── SegmentSummary.tsx
│       ├── InequalityChart.tsx
│       ├── BurnRateGauge.tsx
│       └── InsightsList.tsx
│
├── services/
│   └── cbsApiV10.ts             ← V10 API client (dynamic)
│
└── hooks/
    └── useCBSDataV10.ts         ← V10 React Query hooks (dynamic)
```

---

## Questions?

**Q: Why keep archived code if it's obsolete?**
**A:** For learning and historical context. Future developers can see how the architecture evolved.

**Q: Can I use synthetic pages for testing?**
**A:** No. V10 is 100% real CBS data. Use backend test endpoints for testing.

**Q: What if I need to add a new segment type?**
**A:** V10 is designed for this! Just add the CBS file to backend ETL config. Frontend auto-updates.

---

**Status:** Archive complete ✅
**Next Step:** Phase 5 frontend implementation
**Documentation:** See `/PHASE_5_COMPLETE_IMPLEMENTATION_GUIDE.md`
