# V9 Frontend Pipeline Documentation

## Overview

React + TypeScript frontend for visualizing CBS household expenditure insights from V9 backend API.

**Status**: 🚧 NEEDS UPDATE FOR V9 ENDPOINTS

---

## Current Frontend Structure

```
frontend2/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx       # Main overview page
│   │   ├── Revenue.tsx         # Category analysis
│   │   ├── Customers.tsx       # Quintile segmentation
│   │   └── Products.tsx        # Product performance
│   ├── components/
│   │   ├── BusinessInsight.tsx # Reusable insight cards
│   │   ├── CategoryPieChart.tsx
│   │   └── MetricCard.tsx
│   ├── hooks/
│   │   └── useCBSData.ts       # React Query hooks for API
│   └── services/
│       └── cbsApi.ts           # Axios API client
└── package.json
```

---

## API Integration Requirements

### Old Endpoints (DEPRECATED)
```typescript
// ❌ OLD - These don't exist in V9
GET /api/cbs/quintiles
GET /api/cbs/categories
GET /api/cbs/insights
GET /api/cbs/cities
```

### New V9 Endpoints (REQUIRED)
```typescript
// ✅ NEW - V9 Strategic Endpoints
GET /api/strategic/inequality-gap
GET /api/strategic/burn-rate
GET /api/strategic/fresh-food-battle
GET /api/strategic/retail-competition
GET /api/strategic/household-profiles
GET /api/strategic/expenditures?limit=100
```

---

## Step 1: Update API Client

### File: `frontend2/src/services/cbsApi.ts`

**Current (OLD):**
```typescript
export const getCBSQuintiles = async () => {
  const response = await axios.get('/api/cbs/quintiles');
  return response.data;
};
```

**Required (NEW):**
```typescript
// V9 Strategic API Client
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const cbsApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Endpoint 1: Inequality Gap
export const getInequalityGap = async () => {
  const response = await cbsApi.get('/api/strategic/inequality-gap');
  return response.data;
};

// Endpoint 2: Burn Rate
export const getBurnRate = async () => {
  const response = await cbsApi.get('/api/strategic/burn-rate');
  return response.data;
};

// Endpoint 3: Fresh Food Battle
export const getFreshFoodBattle = async () => {
  const response = await cbsApi.get('/api/strategic/fresh-food-battle');
  return response.data;
};

// Endpoint 4: Retail Competition
export const getRetailCompetition = async () => {
  const response = await cbsApi.get('/api/strategic/retail-competition');
  return response.data;
};

// Endpoint 5: Household Profiles
export const getHouseholdProfiles = async () => {
  const response = await cbsApi.get('/api/strategic/household-profiles');
  return response.data;
};

// Endpoint 6: Expenditures
export const getExpenditures = async (limit = 100) => {
  const response = await cbsApi.get(`/api/strategic/expenditures?limit=${limit}`);
  return response.data;
};

export default cbsApi;
```

---

## Step 2: Update React Query Hooks

### File: `frontend2/src/hooks/useCBSData.ts`

**Required (NEW):**
```typescript
import { useQuery } from '@tanstack/react-query';
import * as cbsApi from '../services/cbsApi';

// Hook 1: Inequality Gap
export const useInequalityGap = () => {
  return useQuery({
    queryKey: ['inequality-gap'],
    queryFn: cbsApi.getInequalityGap,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook 2: Burn Rate
export const useBurnRate = () => {
  return useQuery({
    queryKey: ['burn-rate'],
    queryFn: cbsApi.getBurnRate,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook 3: Fresh Food Battle
export const useFreshFoodBattle = () => {
  return useQuery({
    queryKey: ['fresh-food-battle'],
    queryFn: cbsApi.getFreshFoodBattle,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook 4: Retail Competition
export const useRetailCompetition = () => {
  return useQuery({
    queryKey: ['retail-competition'],
    queryFn: cbsApi.getRetailCompetition,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook 5: Household Profiles
export const useHouseholdProfiles = () => {
  return useQuery({
    queryKey: ['household-profiles'],
    queryFn: cbsApi.getHouseholdProfiles,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook 6: Expenditures
export const useExpenditures = (limit = 100) => {
  return useQuery({
    queryKey: ['expenditures', limit],
    queryFn: () => cbsApi.getExpenditures(limit),
    staleTime: 5 * 60 * 1000,
  });
};
```

---

## Step 3: Update Dashboard Page

### File: `frontend2/src/pages/Dashboard.tsx`

**Required Structure:**

```typescript
import React from 'react';
import { useInequalityGap, useBurnRate, useFreshFoodBattle } from '../hooks/useCBSData';
import BusinessInsight from '../components/BusinessInsight';
import MetricCard from '../components/MetricCard';

const Dashboard: React.FC = () => {
  const { data: inequalityData, isLoading: inequalityLoading } = useInequalityGap();
  const { data: burnRateData, isLoading: burnRateLoading } = useBurnRate();
  const { data: freshFoodData, isLoading: freshFoodLoading } = useFreshFoodBattle();

  if (inequalityLoading || burnRateLoading || freshFoodLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>MarketPulse V9 - CBS Household Expenditure Insights</h1>

      {/* Key Metrics */}
      <div className="metrics-row">
        <MetricCard
          title="Highest Inequality"
          value={`${inequalityData?.top_gaps[0]?.gap_ratio.toFixed(1)}x`}
          subtitle={inequalityData?.top_gaps[0]?.item_name}
          variant="danger"
        />
        <MetricCard
          title="Q1 Burn Rate"
          value={`${burnRateData?.q1_burn_rate_pct.toFixed(1)}%`}
          subtitle="Financial Crisis Level"
          variant="warning"
        />
        <MetricCard
          title="Traditional Retail Wins"
          value={freshFoodData?.categories.filter(c => c.winner === 'Traditional Wins').length}
          subtitle="Out of 14 food categories"
          variant="success"
        />
      </div>

      {/* Business Insights */}
      <div className="insights-row">
        <BusinessInsight
          title="Inequality Gap Analysis"
          description={inequalityData?.insight}
          variant="primary"
        />
        <BusinessInsight
          title="Burn Rate Analysis"
          description={burnRateData?.insight}
          variant="warning"
        />
        <BusinessInsight
          title="Retail Battle"
          description={freshFoodData?.insight}
          variant="success"
        />
      </div>
    </div>
  );
};

export default Dashboard;
```

---

## Step 4: Update Revenue Page

### File: `frontend2/src/pages/Revenue.tsx`

**Purpose**: Show retail competition with 8 store types

```typescript
import React from 'react';
import { useRetailCompetition } from '../hooks/useCBSData';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Revenue: React.FC = () => {
  const { data, isLoading } = useRetailCompetition();

  if (isLoading) return <div>Loading...</div>;

  // Transform data for stacked bar chart
  const chartData = data?.categories.map(cat => ({
    category: cat.category,
    'Supermarket Chain': cat.supermarket_chain_pct,
    'Market': cat.market_pct,
    'Grocery': cat.grocery_pct,
    'Special Shop': cat.special_shop_pct,
    'Butcher': cat.butcher_pct,
    'Veg/Fruit Shop': cat.veg_fruit_shop_pct,
    'Online': cat.online_supermarket_pct,
    'Other': cat.other_pct,
  }));

  return (
    <div className="revenue-page">
      <h1>Retail Competition - 8 Store Types</h1>
      <ResponsiveContainer width="100%" height={500}>
        <BarChart data={chartData}>
          <XAxis dataKey="category" angle={-45} textAnchor="end" height={150} />
          <YAxis label={{ value: '% Market Share', angle: -90 }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="Supermarket Chain" stackId="a" fill="#3b82f6" />
          <Bar dataKey="Market" stackId="a" fill="#10b981" />
          <Bar dataKey="Grocery" stackId="a" fill="#f59e0b" />
          <Bar dataKey="Special Shop" stackId="a" fill="#8b5cf6" />
          <Bar dataKey="Butcher" stackId="a" fill="#ef4444" />
          <Bar dataKey="Veg/Fruit Shop" stackId="a" fill="#14b8a6" />
          <Bar dataKey="Online" stackId="a" fill="#6366f1" />
          <Bar dataKey="Other" stackId="a" fill="#9ca3af" />
        </BarChart>
      </ResponsiveContainer>

      <div className="insight-box">
        <h3>Key Insights:</h3>
        <ul>
          <li>Supermarket chains dominate packaged goods (60%+)</li>
          <li>Butchers lead in fresh meat (45.1%)</li>
          <li>Markets capture 28-37% of fresh produce</li>
          <li>Special shops control 30% of alcoholic beverages</li>
        </ul>
      </div>
    </div>
  );
};

export default Revenue;
```

---

## Step 5: Update Customers Page

### File: `frontend2/src/pages/Customers.tsx`

**Purpose**: Show expenditure inequality by quintile

```typescript
import React from 'react';
import { useInequalityGap } from '../hooks/useCBSData';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Customers: React.FC = () => {
  const { data, isLoading } = useInequalityGap();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="customers-page">
      <h1>Inequality Gap Analysis</h1>

      <div className="top-gaps">
        <h2>Top 10 Spending Inequalities (Q5/Q1 Ratio)</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data?.top_gaps} layout="vertical">
            <XAxis type="number" label="Q5/Q1 Spending Ratio" />
            <YAxis type="category" dataKey="item_name" width={200} />
            <Tooltip />
            <Bar dataKey="gap_ratio" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="insight-box">
        <h3>Business Insight:</h3>
        <p>{data?.insight}</p>
      </div>

      <div className="recommendations">
        <h3>Marketing Recommendations:</h3>
        <ul>
          <li>Allocate 40-45% of marketing budget to Q4-Q5 segments</li>
          <li>Create 3 product tiers: Premium (Q5), Value (Q2-Q3), Essential (Q1)</li>
          <li>Q5 segments are price-insensitive - focus on quality and experience</li>
        </ul>
      </div>
    </div>
  );
};

export default Customers;
```

---

## Step 6: Update Products Page

### File: `frontend2/src/pages/Products.tsx`

**Purpose**: Show all expenditure categories

```typescript
import React, { useState } from 'react';
import { useExpenditures } from '../hooks/useCBSData';

const Products: React.FC = () => {
  const [limit, setLimit] = useState(50);
  const { data, isLoading } = useExpenditures(limit);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="products-page">
      <h1>Household Expenditures</h1>
      <p>Showing {data?.expenditures.length} of {data?.total_categories} categories</p>

      <div className="controls">
        <button onClick={() => setLimit(50)}>Top 50</button>
        <button onClick={() => setLimit(100)}>Top 100</button>
        <button onClick={() => setLimit(528)}>All Categories</button>
      </div>

      <table className="expenditure-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Q5 (Rich)</th>
            <th>Q1 (Poor)</th>
            <th>Total Spend</th>
            <th>Inequality Index</th>
          </tr>
        </thead>
        <tbody>
          {data?.expenditures.map((item, idx) => (
            <tr key={idx}>
              <td>{item.item_name}</td>
              <td>{item.q5_spend.toFixed(1)} NIS</td>
              <td>{item.q1_spend.toFixed(1)} NIS</td>
              <td>{item.total_spend.toFixed(1)} NIS</td>
              <td>
                <span className={item.inequality_index > 5 ? 'high-inequality' : ''}>
                  {item.inequality_index.toFixed(2)}x
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="insight-box">
        <h3>Data Insights:</h3>
        <p>{data?.insight}</p>
      </div>
    </div>
  );
};

export default Products;
```

---

## TypeScript Interfaces

### File: `frontend2/src/types/api.ts` (NEW)

```typescript
// Inequality Gap Types
export interface InequalityGapItem {
  item_name: string;
  rich_spend: number;
  poor_spend: number;
  gap_ratio: number;
  total_spend: number;
}

export interface InequalityGapResponse {
  top_gaps: InequalityGapItem[];
  insight: string;
}

// Burn Rate Types
export interface BurnRateResponse {
  q5_burn_rate_pct: number;
  q4_burn_rate_pct: number;
  q3_burn_rate_pct: number;
  q2_burn_rate_pct: number;
  q1_burn_rate_pct: number;
  total_burn_rate_pct: number;
  insight: string;
}

// Fresh Food Battle Types
export interface FreshFoodBattleItem {
  category: string;
  traditional_retail_pct: number;
  supermarket_chain_pct: number;
  traditional_advantage: number;
  winner: 'Traditional Wins' | 'Supermarket Wins';
}

export interface FreshFoodBattleResponse {
  categories: FreshFoodBattleItem[];
  insight: string;
}

// Retail Competition Types
export interface RetailCompetitionItem {
  category: string;
  other_pct: number;
  special_shop_pct: number;
  butcher_pct: number;
  veg_fruit_shop_pct: number;
  online_supermarket_pct: number;
  supermarket_chain_pct: number;
  market_pct: number;
  grocery_pct: number;
  total_pct: number;
}

export interface RetailCompetitionResponse {
  categories: RetailCompetitionItem[];
  insight: string;
}

// Household Profiles Types
export interface HouseholdProfileItem {
  metric_name: string;
  q5_val: number;
  q4_val: number;
  q3_val: number;
  q2_val: number;
  q1_val: number;
  total_val: number;
}

export interface HouseholdProfilesResponse {
  profiles: HouseholdProfileItem[];
  insight: string;
}

// Expenditures Types
export interface ExpenditureItem {
  item_name: string;
  q5_spend: number;
  q4_spend: number;
  q3_spend: number;
  q2_spend: number;
  q1_spend: number;
  total_spend: number;
  inequality_index: number;
}

export interface ExpendituresResponse {
  expenditures: ExpenditureItem[];
  total_categories: number;
  insight: string;
}
```

---

## Testing Frontend

### Step 1: Install Dependencies
```bash
cd frontend2
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

**Expected**: Server runs on `http://localhost:5173`

### Step 3: Verify Backend Connection

Open browser console and check for:
- ✅ No CORS errors
- ✅ API calls return 200 OK
- ✅ Data renders on page

### Step 4: Test Each Page

**Dashboard:**
- [ ] Shows 3 metric cards
- [ ] Shows 3 business insights
- [ ] All numbers match backend API responses

**Revenue:**
- [ ] Shows stacked bar chart with 8 store types
- [ ] All 14 food categories visible
- [ ] Alcoholic beverages shows: Supermarket 51.1%, Special Shop 30.4%

**Customers:**
- [ ] Shows top 10 inequality gaps
- [ ] Domestic help at #1 with 18.11x ratio
- [ ] Business recommendations displayed

**Products:**
- [ ] Shows expenditure table
- [ ] Can toggle between 50/100/All categories
- [ ] Sorting works correctly

---

## Current Issues (TO FIX)

### Issue 1: Old API Endpoints
**Problem**: Frontend still calls `/api/cbs/*` which don't exist
**Solution**: Update all API calls to `/api/strategic/*`

### Issue 2: Missing TypeScript Types
**Problem**: No type definitions for V9 API responses
**Solution**: Create `frontend2/src/types/api.ts` with all interfaces

### Issue 3: Chart Data Format
**Problem**: Charts expect old data structure
**Solution**: Transform V9 API responses to match chart requirements

### Issue 4: Hebrew RTL Support
**Problem**: Some text may not render correctly
**Solution**: Add `dir="rtl"` to Hebrew text elements

---

## Next Steps

1. ✅ Document V9 API endpoints
2. ⏳ Update `cbsApi.ts` with new endpoints
3. ⏳ Update `useCBSData.ts` hooks
4. ⏳ Update all 4 pages (Dashboard, Revenue, Customers, Products)
5. ⏳ Add TypeScript interfaces
6. ⏳ Test frontend with live backend
7. ⏳ Fix any CORS issues
8. ⏳ Deploy to production

---

## Deployment Checklist

### Before Deploying:
- [ ] Update API_BASE_URL to production URL
- [ ] Enable production CORS origins in backend
- [ ] Test all pages work with production API
- [ ] Verify Hebrew text renders correctly
- [ ] Check mobile responsiveness
- [ ] Run `npm run build` successfully
- [ ] Test built files with `npm run preview`

### Production Environment Variables:
```
VITE_API_BASE_URL=https://api.marketpulse.com  # Production API URL
```

---

## Performance Considerations

- **API Caching**: React Query caches for 5 minutes
- **Bundle Size**: Keep under 500KB gzipped
- **Code Splitting**: Lazy load pages
- **Image Optimization**: Use WebP format
- **CDN**: Serve static assets from CDN
