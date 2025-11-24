import { ProductData, CategoryBreakdown, RevenueData, CustomerData } from './types';
import { formatCurrency, formatPercent } from './utils/hebrew';

export interface Insight {
  type: 'success' | 'warning' | 'info' | 'error';
  title: string;
  description: string;
  metric?: string;
}

export function analyzeProducts(products: ProductData[]): Insight[] {
  const insights: Insight[] = [];
  
  if (products.length === 0) return insights;

  // Top performer
  const topProduct = products.reduce((prev, current) => 
    current.revenue > prev.revenue ? current : prev
  );
  
  insights.push({
    type: 'success',
    title: 'מוצר מוביל',
    description: `${topProduct.name} מייצר את ההכנסה הגבוהה ביותר עם ${topProduct.unitsSold.toLocaleString('he-IL')} יחידות שנמכרו`,
    metric: formatCurrency(topProduct.revenue)
  });

  // Declining products
  const decliningProducts = products.filter(p => p.trend === 'down');
  if (decliningProducts.length > 0) {
    insights.push({
      type: 'warning',
      title: 'דורש תשומת לב',
      description: `${decliningProducts.length} מוצרים במגמת ירידה - שקול קמפיין שיווקי או בדיקת תמחור`,
      metric: `${decliningProducts.length} מוצרים`
    });
  }

  // Growth opportunities
  const growingProducts = products.filter(p => p.trend === 'up');
  if (growingProducts.length > 0) {
    insights.push({
      type: 'success',
      title: 'הזדמנויות צמיחה',
      description: `${growingProducts.length} מוצרים במגמת עלייה - הזדמנות להגדלת מלאי ושיווק ממוקד`,
      metric: `${growingProducts.length} מוצרים`
    });
  }

  // Revenue concentration
  const totalRevenue = products.reduce((sum, p) => sum + p.revenue, 0);
  const topThreeRevenue = products
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 3)
    .reduce((sum, p) => sum + p.revenue, 0);
  const concentration = (topThreeRevenue / totalRevenue) * 100;

  if (concentration > 70) {
    insights.push({
      type: 'warning',
      title: 'ריכוז הכנסות גבוה',
      description: `3 המוצרים המובילים מייצרים ${concentration.toFixed(1)}% מההכנסות - שקול גיוון`,
      metric: formatPercent(concentration / 100)
    });
  } else {
    insights.push({
      type: 'success',
      title: 'גיוון הכנסות בריא',
      description: `הכנסות מפוזרות היטב בין מוצרים שונים - סיכון נמוך`,
      metric: formatPercent(concentration / 100)
    });
  }

  return insights;
}

export function analyzeCategories(categories: CategoryBreakdown[]): Insight[] {
  const insights: Insight[] = [];
  
  if (categories.length === 0) return insights;

  // Top category
  const topCategory = categories.reduce((prev, current) => 
    current.value > prev.value ? current : prev
  );
  
  insights.push({
    type: 'success',
    title: 'קטגוריה מובילה',
    description: `${topCategory.category} היא הקטגוריה בעלת הביצועים הגבוהים ביותר`,
    metric: `${formatCurrency(topCategory.value)} (${formatPercent(topCategory.percentage / 100)})`
  });

  // Long tail analysis
  const smallCategories = categories.filter(c => c.percentage < 5);
  if (smallCategories.length > 0) {
    const longTailRevenue = smallCategories.reduce((sum, c) => sum + c.value, 0);
    insights.push({
      type: 'info',
      title: 'זנב ארוך',
      description: `${smallCategories.length} קטגוריות קטנות תורמות יחד ${formatCurrency(longTailRevenue)} - שקול איחוד או הסרה`,
      metric: `${smallCategories.length} קטגוריות`
    });
  }

  // Balanced distribution
  const topThree = categories.slice(0, 3).reduce((sum, c) => sum + c.percentage, 0);
  if (topThree < 60) {
    insights.push({
      type: 'success',
      title: 'חלוקה מאוזנת',
      description: 'הכנסות מפוזרות באופן שווה בין קטגוריות - פורטפוליו מגוון',
      metric: 'סיכון נמוך'
    });
  } else if (topThree > 80) {
    insights.push({
      type: 'warning',
      title: 'תלות גבוהה',
      description: '3 קטגוריות מובילות תורמות מעל 80% מההכנסות - סיכון ריכוז',
      metric: formatPercent(topThree / 100)
    });
  }

  return insights;
}

export function analyzeRevenue(revenueData: RevenueData[]): Insight[] {
  const insights: Insight[] = [];
  
  if (revenueData.length < 2) return insights;

  // Calculate growth trend
  const sortedData = [...revenueData].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );
  
  const firstHalf = sortedData.slice(0, Math.floor(sortedData.length / 2));
  const secondHalf = sortedData.slice(Math.floor(sortedData.length / 2));
  
  const firstHalfAvg = firstHalf.reduce((sum, d) => sum + d.revenue, 0) / firstHalf.length;
  const secondHalfAvg = secondHalf.reduce((sum, d) => sum + d.revenue, 0) / secondHalf.length;
  
  const growthRate = ((secondHalfAvg - firstHalfAvg) / firstHalfAvg) * 100;

  if (growthRate > 5) {
    insights.push({
      type: 'success',
      title: 'מגמת צמיחה חיובית',
      description: `הכנסות גדלות בממוצע ב-${growthRate.toFixed(1)}% - המשך בכיוון הנוכחי`,
      metric: `+${growthRate.toFixed(1)}%`
    });
  } else if (growthRate < -5) {
    insights.push({
      type: 'warning',
      title: 'מגמת ירידה',
      description: `הכנסות יורדות בממוצע ב-${Math.abs(growthRate).toFixed(1)}% - נדרשת התערבות`,
      metric: `${growthRate.toFixed(1)}%`
    });
  } else {
    insights.push({
      type: 'info',
      title: 'הכנסות יציבות',
      description: 'הכנסות נשארות יציבות ללא שינוי משמעותי',
      metric: 'יציב'
    });
  }

  // Detect anomalies (days with unusual revenue)
  const avgRevenue = sortedData.reduce((sum, d) => sum + d.revenue, 0) / sortedData.length;
  const stdDev = Math.sqrt(
    sortedData.reduce((sum, d) => sum + Math.pow(d.revenue - avgRevenue, 2), 0) / sortedData.length
  );
  
  const anomalies = sortedData.filter(d => 
    Math.abs(d.revenue - avgRevenue) > stdDev * 2
  );

  if (anomalies.length > 0) {
    const highestAnomaly = anomalies.reduce((prev, current) => 
      Math.abs(current.revenue - avgRevenue) > Math.abs(prev.revenue - avgRevenue) ? current : prev
    );
    
    insights.push({
      type: 'info',
      title: 'חריגה זוהתה',
      description: `יום ${highestAnomaly.hebrewDate} הראה הכנסה חריגה - בדוק אירועים מיוחדים`,
      metric: formatCurrency(highestAnomaly.revenue)
    });
  }

  // Best day
  const bestDay = sortedData.reduce((prev, current) => 
    current.revenue > prev.revenue ? current : prev
  );
  
  insights.push({
    type: 'success',
    title: 'יום הכנסות שיא',
    description: `${bestDay.dayName}, ${bestDay.hebrewDate} היה היום עם ההכנסות הגבוהות ביותר`,
    metric: formatCurrency(bestDay.revenue)
  });

  return insights;
}

export function analyzeCustomers(customers: CustomerData[]): Insight[] {
  const insights: Insight[] = [];
  
  if (customers.length === 0) return insights;

  // Top customer
  const topCustomer = customers.reduce((prev, current) => 
    current.totalSpent > prev.totalSpent ? current : prev
  );
  
  insights.push({
    type: 'success',
    title: 'לקוח VIP',
    description: `${topCustomer.name} הוא הלקוח בעל הערך הגבוה ביותר עם ${topCustomer.transactionCount} עסקאות`,
    metric: formatCurrency(topCustomer.totalSpent)
  });

  // Average customer value
  const avgSpent = customers.reduce((sum, c) => sum + c.totalSpent, 0) / customers.length;
  const highValueCustomers = customers.filter(c => c.totalSpent > avgSpent * 2);
  
  insights.push({
    type: 'info',
    title: 'לקוחות בעלי ערך גבוה',
    description: `${highValueCustomers.length} לקוחות מוציאים פי 2 מהממוצע - התמקד בשימור`,
    metric: `${highValueCustomers.length} לקוחות`
  });

  // Geographic concentration
  const cityCounts = customers.reduce((acc, c) => {
    acc[c.city] = (acc[c.city] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const topCity = Object.entries(cityCounts).reduce((prev, current) => 
    current[1] > prev[1] ? current : prev
  );
  
  insights.push({
    type: 'info',
    title: 'ריכוז גיאוגרפי',
    description: `${topCity[0]} היא העיר עם מספר הלקוחות הגבוה ביותר`,
    metric: `${topCity[1]} לקוחות`
  });

  // Transaction frequency
  const avgTransactions = customers.reduce((sum, c) => sum + c.transactionCount, 0) / customers.length;
  const frequentBuyers = customers.filter(c => c.transactionCount > avgTransactions * 1.5);
  
  if (frequentBuyers.length > 0) {
    insights.push({
      type: 'success',
      title: 'לקוחות נאמנים',
      description: `${frequentBuyers.length} לקוחות מבצעים רכישות חוזרות באופן תדיר - תכנית נאמנות מומלצת`,
      metric: `${frequentBuyers.length} לקוחות`
    });
  }

  return insights;
}
