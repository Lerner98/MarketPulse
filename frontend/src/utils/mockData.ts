import type { SankeyData } from '@/types'

// Mock data for Customer Journey Sankey diagram
// In production, this would come from the API
export const mockCustomerJourneyData: SankeyData = {
  nodes: [
    // Sources (Traffic channels)
    { name: 'Direct', category: 'source' },
    { name: 'Organic Search', category: 'source' },
    { name: 'Paid Ads', category: 'source' },
    { name: 'Social Media', category: 'source' },
    { name: 'Email', category: 'source' },

    // Middle stage (Product categories)
    { name: 'Electronics', category: 'category' },
    { name: 'Fashion', category: 'category' },
    { name: 'Home & Garden', category: 'category' },
    { name: 'Books', category: 'category' },

    // End stage (Outcomes)
    { name: 'Purchase', category: 'outcome' },
    { name: 'Browse Only', category: 'outcome' },
  ],
  links: [
    // Direct traffic
    { source: 0, target: 5, value: 120 }, // Direct -> Electronics
    { source: 0, target: 6, value: 80 },  // Direct -> Fashion
    { source: 0, target: 7, value: 40 },  // Direct -> Home & Garden

    // Organic Search
    { source: 1, target: 5, value: 200 }, // Organic -> Electronics
    { source: 1, target: 6, value: 150 }, // Organic -> Fashion
    { source: 1, target: 8, value: 100 }, // Organic -> Books
    { source: 1, target: 10, value: 180 }, // Organic -> Browse Only

    // Paid Ads
    { source: 2, target: 5, value: 180 }, // Paid -> Electronics
    { source: 2, target: 6, value: 220 }, // Paid -> Fashion

    // Social Media
    { source: 3, target: 6, value: 160 }, // Social -> Fashion
    { source: 3, target: 7, value: 90 },  // Social -> Home & Garden
    { source: 3, target: 10, value: 120 }, // Social -> Browse Only

    // Email
    { source: 4, target: 5, value: 100 }, // Email -> Electronics
    { source: 4, target: 8, value: 60 },  // Email -> Books

    // Categories to outcomes
    { source: 5, target: 9, value: 450 },  // Electronics -> Purchase
    { source: 5, target: 10, value: 150 }, // Electronics -> Browse
    { source: 6, target: 9, value: 400 },  // Fashion -> Purchase
    { source: 6, target: 10, value: 210 }, // Fashion -> Browse
    { source: 7, target: 9, value: 100 },  // Home -> Purchase
    { source: 7, target: 10, value: 30 },  // Home -> Browse
    { source: 8, target: 9, value: 140 },  // Books -> Purchase
    { source: 8, target: 10, value: 20 },  // Books -> Browse
  ],
}
