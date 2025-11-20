# MarketPulse Frontend

Modern React frontend for the MarketPulse e-commerce analytics platform.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Chart library
- **D3.js** - Advanced visualizations
- **Vitest** - Unit testing
- **React Testing Library** - Component testing
- **Playwright** - E2E testing

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
```

### Testing

```bash
# Unit and integration tests
npm test

# Test UI
npm run test:ui

# E2E tests
npm run test:e2e

# Coverage
npm run coverage
```

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Route components
├── visualizations/  # D3.js visualizations
├── hooks/           # Custom React hooks
├── api/             # API client
├── utils/           # Helper functions
├── types/           # TypeScript types
└── test/            # Test utilities
```

## API Integration

The frontend proxies `/api/*` requests to the backend at `http://localhost:8000`.

Available endpoints:
- `GET /api/health` - Health check
- `GET /api/dashboard` - Dashboard metrics
- `GET /api/revenue?limit=7` - Revenue data
- `GET /api/customers?limit=10&sort=total_spent` - Top customers
- `GET /api/products` - Product performance

## Performance Targets

- Initial load: <2 seconds
- Time to Interactive: <3 seconds
- Lighthouse score: 90+
- Bundle size: <500KB gzipped

## License

MIT
