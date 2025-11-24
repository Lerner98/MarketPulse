import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Menu, BarChart3 } from 'lucide-react';
import { GLOBAL_STYLES } from '@/lib/globals';
import { cn } from '@/lib/utils';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';

interface AppLayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'לוח בקרה', href: '/', icon: LayoutDashboard },
  { name: 'כל הגרפים', href: '/charts', icon: BarChart3 },
  // V10: Only dashboard is implemented with normalized star schema
  // Other pages will be added as needed with V10 architecture
];

export const AppLayout = ({ children }: AppLayoutProps) => {
  const location = useLocation();

  const NavLinks = () => (
    <>
      {navigation.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.href;
        return (
          <Link
            key={item.name}
            to={item.href}
            className={cn(
              GLOBAL_STYLES.navigation.link,
              isActive ? GLOBAL_STYLES.navigation.linkActive : GLOBAL_STYLES.navigation.linkInactive
            )}
          >
            <Icon className="w-5 h-5" />
            <span>{item.name}</span>
          </Link>
        );
      })}
    </>
  );

  return (
    <div className="min-h-screen bg-background" dir="rtl">
      {/* Header */}
      <header className={GLOBAL_STYLES.layouts.header}>
        <div className="h-16 flex items-center justify-between px-4 md:pr-4 md:pl-[calc(256px+1rem)]">
          <div className="flex items-center gap-4">
            <Sheet>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon">
                  <Menu className="w-6 h-6" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-64" dir="rtl">
                <nav className="flex flex-col gap-2 mt-8">
                  <NavLinks />
                </nav>
              </SheetContent>
            </Sheet>
            <h1 className="text-2xl font-bold text-primary">MarketPulse</h1>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar - Desktop */}
        <aside className="hidden md:block w-64 border-l border-border bg-card fixed h-[calc(100vh-4rem)] top-16 right-0 overflow-y-auto">
          <nav className="p-4 space-y-2">
            <NavLinks />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 md:mr-64 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
