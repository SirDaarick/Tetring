/** Barra lateral de navegación principal.
 *
 * Desktop: sidebar fijo. Tablet: colapsado a íconos. Mobile: Sheet.
 */
import type { ReactElement } from "react";
import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  Brain,
  Home,
  LogOut,
  Menu,
  Save,
  Settings,
  Square,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

interface SidebarItem {
  to: string;
  icon: typeof Home;
  label: string;
}

const SIDEBAR_ITEMS: SidebarItem[] = [
  { to: "/dashboard", icon: Home, label: "Inicio" },
  { to: "/scheduler", icon: Brain, label: "Generar" },
  { to: "/saved", icon: Save, label: "Guardados" },
];

const BOTTOM_ITEMS: SidebarItem[] = [
  { to: "/profile", icon: Settings, label: "Perfil" },
];

function SidebarContent({
  isCollapsed,
  onItemClick,
}: {
  isCollapsed: boolean;
  onItemClick?: () => void;
}): ReactElement {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout(): void {
    logout();
    navigate("/login", { replace: true });
    onItemClick?.();
  }

  return (
    <div className="flex h-full flex-col bg-[#f4f1fa] py-6">
      <div className="mb-8 flex items-center gap-3 px-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-clay-primary-soft to-clay-primary text-white shadow-clay">
          <Square className="h-5 w-5" />
        </div>
        {!isCollapsed && (
          <span className="text-xl font-bold text-clay-text">TETRING</span>
        )}
      </div>

      <nav className="flex-1 space-y-2 px-3">
        {SIDEBAR_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onItemClick}
            className={({ isActive }) =>
              `
                flex items-center gap-3 rounded-clay px-4 py-3 transition-all duration-200
                focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2
                ${isActive ? "bg-clay-surface text-clay-primary shadow-clay" : "text-clay-text-secondary hover:bg-[#f5f0ff]"}
                ${isCollapsed ? "justify-center px-2" : ""}
              `
            }
            aria-label={item.label}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span className="font-medium">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="space-y-2 px-3">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onItemClick}
            className={({ isActive }) =>
              `
                flex items-center gap-3 rounded-clay px-4 py-3 transition-all duration-200
                focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2
                ${isActive ? "bg-clay-surface text-clay-primary shadow-clay" : "text-clay-text-secondary hover:bg-[#f5f0ff]"}
                ${isCollapsed ? "justify-center px-2" : ""}
              `
            }
            aria-label={item.label}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span className="font-medium">{item.label}</span>}
          </NavLink>
        ))}

        <Button
          variant="ghost"
          onClick={handleLogout}
          className="w-full justify-start gap-3 rounded-clay px-4 py-3 text-clay-text-secondary hover:bg-[#f5f0ff] hover:text-clay-error focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {!isCollapsed && <span className="font-medium">Salir</span>}
        </Button>
      </div>
    </div>
  );
}

export function Sidebar(): ReactElement {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile */}
      <div className="fixed left-4 top-4 z-40 lg:hidden">
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger>
            <Button
              variant="outline"
              size="icon"
              className="rounded-clay border-clay-border bg-white/70 shadow-clay backdrop-blur-md"
              aria-label="Abrir menú"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent
            side="left"
            className="w-[260px] border-r-0 bg-[#f4f1fa] p-0"
          >
            <SidebarContent isCollapsed={false} onItemClick={() => setMobileOpen(false)} />
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:flex lg:w-60 lg:flex-col">
        <SidebarContent isCollapsed={false} />
      </aside>

      {/* Tablet collapsed */}
      <aside className="hidden md:fixed md:inset-y-0 md:left-0 md:z-30 md:flex md:w-20 md:flex-col lg:hidden">
        <SidebarContent isCollapsed />
      </aside>
    </>
  );
}
