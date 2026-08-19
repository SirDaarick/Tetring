/** Barra lateral de navegación principal.
 *
 * Desktop: sidebar abatible (w-60 o w-20). Mobile: Sheet.
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
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/stores/auth-store";
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
      <div className={`mb-8 flex items-center gap-3 px-5 transition-all duration-300 ${isCollapsed ? "justify-center" : ""}`}>
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-clay-primary-soft to-clay-primary text-white shadow-clay">
          <Square className="h-5 w-5" />
        </div>
        {!isCollapsed && (
          <span className="text-xl font-bold text-clay-text tracking-wide truncate">TETRING</span>
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
            {!isCollapsed && <span className="font-medium truncate">{item.label}</span>}
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
            {!isCollapsed && <span className="font-medium truncate">{item.label}</span>}
          </NavLink>
        ))}

        <Button
          variant="ghost"
          onClick={handleLogout}
          className={`w-full gap-3 rounded-clay px-4 py-3 text-clay-text-secondary hover:bg-[#f5f0ff] hover:text-clay-error focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2 ${
            isCollapsed ? "justify-center px-2" : "justify-start"
          }`}
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {!isCollapsed && <span className="font-medium truncate">Salir</span>}
        </Button>
      </div>
    </div>
  );
}

export function Sidebar(): ReactElement {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const sidebarCollapsed = useAuthStore((state) => state.sidebarCollapsed);
  const toggleSidebar = useAuthStore((state) => state.toggleSidebar);

  // Por defecto se mantiene compacta (iconos) y al pasar el mouse por encima se expande de inmediato
  const isExpanded = isHovered || !sidebarCollapsed;

  return (
    <>
      {/* Mobile Menu Button & Drawer */}
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

      {/* Desktop / Tablet Hover-expanding Sidebar */}
      <aside
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`hidden md:flex md:flex-col md:h-screen md:sticky md:top-0 md:z-40 border-r border-clay-border/10 bg-[#f4f1fa] transition-all duration-300 ease-in-out shrink-0 ${
          isExpanded ? "w-60 shadow-2xl shadow-clay-primary/15" : "w-20"
        }`}
      >
        <SidebarContent isCollapsed={!isExpanded} />

        {/* Botón flotante para fijar o desfijar el menú abierto */}
        <button
          type="button"
          onClick={toggleSidebar}
          className="hidden lg:flex absolute right-[-14px] top-12 z-50 h-7 w-7 items-center justify-center rounded-full border border-clay-border bg-white text-clay-text shadow-clay hover:bg-clay-surface hover:-translate-y-0.5 active:scale-[0.9] transition-all duration-300"
          title={sidebarCollapsed ? "Fijar menú siempre abierto" : "Colapsar menú (expandir con mouse)"}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4 text-clay-primary" />
          ) : (
            <ChevronLeft className="h-4 w-4 text-clay-primary" />
          )}
        </button>
      </aside>
    </>
  );
}
