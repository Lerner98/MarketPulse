# Deprecated Recharts Components

**Date Archived**: 2024-11-22
**Reason**: Recharts has poor RTL/Hebrew text support causing persistent label positioning issues
**Migration Status**: ✅ ALL 4 COMPONENTS SUCCESSFULLY MIGRATED TO CHART.JS

## Components Archived:

1. ✅ **CategoryComparisonChart.tsx** - Bar chart for income vs spending comparison
2. ✅ **SegmentComparisonChart.tsx** - Line chart for trend analysis
3. ✅ **InequalityChart.tsx** - Horizontal bar chart for inequality analysis
4. ✅ **BurnRateGauge.tsx** - Pie chart for burn rate visualization

## Issues Encountered:

- X-axis labels embedded in chart area instead of below it
- Y-axis labels not properly positioned next to axis
- Hebrew text rendering issues with RTL layout
- Axis title labels overlapping with tick values
- `position: 'insideBottom'` with negative `offset` broken with Hebrew text

## Migration Path:

Replaced with **Chart.js (react-chartjs-2)** for better:
- RTL text support
- Canvas-based rendering (61kb vs 189kb)
- Proper axis label positioning
- Professional chart templates

## If Reversion Needed:

Copy these components back to `frontend/src/components/v10/` and install:
```bash
npm install recharts
```

## Documentation:

See `recharts_rtl_visualization_standard.md` in project root for detailed analysis of Recharts RTL issues.
