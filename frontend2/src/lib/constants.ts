// Design System - Single Source of Truth for MarketPulse Platform

export const SPACING = {
  padding: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '48px',
    '4xl': '64px',
  },
  margin: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '48px',
    '4xl': '64px',
  },
  containers: {
    maxWidth: 'max-w-7xl',
    section: 'py-12 px-4 sm:px-6 lg:px-8',
  },
} as const;

export const COLORS = {
  primary: 'hsl(221, 83%, 53%)', // Blue-600
  secondary: 'hsl(262, 83%, 58%)', // Purple-600
  accent: 'hsl(142, 76%, 36%)', // Emerald-500
  success: 'hsl(142, 76%, 36%)',
  warning: 'hsl(45, 93%, 47%)',
  error: 'hsl(0, 72%, 51%)',
  info: 'hsl(199, 89%, 48%)',
  neutrals: {
    50: 'hsl(210, 40%, 98%)',
    100: 'hsl(214, 32%, 96%)',
    200: 'hsl(213, 27%, 92%)',
    300: 'hsl(212, 24%, 85%)',
    400: 'hsl(214, 20%, 69%)',
    500: 'hsl(215, 16%, 47%)',
    600: 'hsl(215, 19%, 35%)',
    700: 'hsl(215, 25%, 27%)',
    800: 'hsl(217, 33%, 17%)',
    900: 'hsl(222, 47%, 11%)',
  },
} as const;

export const TYPOGRAPHY = {
  fonts: {
    ui: 'Inter, system-ui, -apple-system, sans-serif',
    hebrew: 'Assistant, system-ui, -apple-system, sans-serif',
  },
  sizes: {
    xs: 'text-xs',
    sm: 'text-sm',
    base: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
    '2xl': 'text-2xl',
    '3xl': 'text-3xl',
    '4xl': 'text-4xl',
  },
  weights: {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold',
  },
  lineHeights: {
    tight: 'leading-tight',
    normal: 'leading-normal',
    relaxed: 'leading-relaxed',
  },
  letterSpacing: {
    tight: 'tracking-tight',
    normal: 'tracking-normal',
    wide: 'tracking-wide',
  },
} as const;

export const RTL_SUPPORT = {
  direction: {
    rtl: 'rtl' as const,
    ltr: 'ltr' as const,
  },
  textAlign: {
    start: 'text-start',
    end: 'text-end',
    center: 'text-center',
  },
  marginFlip: {
    mr: 'me-',
    ml: 'ms-',
  },
  paddingFlip: {
    pr: 'pe-',
    pl: 'ps-',
  },
} as const;

export const BORDERS = {
  widths: {
    thin: 'border',
    medium: 'border-2',
    thick: 'border-4',
  },
  radius: {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    '2xl': 'rounded-2xl',
    full: 'rounded-full',
  },
} as const;

export const SHADOWS = {
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  '2xl': 'shadow-2xl',
  none: 'shadow-none',
} as const;

export const ANIMATIONS = {
  durations: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  easing: {
    inOut: 'ease-in-out',
    out: 'ease-out',
    in: 'ease-in',
  },
  transitions: {
    all: 'transition-all',
    colors: 'transition-colors',
    transform: 'transition-transform',
  },
} as const;

export const Z_INDEX = {
  header: 50,
  dropdown: 40,
  modal: 100,
  tooltip: 110,
} as const;

export const BREAKPOINTS = {
  mobile: '640px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1280px',
} as const;

export const UI_LIMITS = {
  chartDataPoints: 1000,
  tableRowsPerPage: [25, 50, 100],
  apiTimeout: 30000, // 30 seconds
} as const;
