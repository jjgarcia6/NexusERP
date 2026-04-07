import { useMemo, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

import { Button } from "../ui/button";
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet";
import { useAuth } from "../../features/auth";
import { useAuthStore } from "../../shared/stores/auth.store";

type NavItem = {
  label: string;
  to: string;
};

export function MainLayout() {
  const location = useLocation();
  const accessToken = useAuthStore((state) => state.accessToken);
  const { user, isAdmin, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = useMemo<NavItem[]>(() => {
    if (!accessToken) {
      return [];
    }
    const baseItems: NavItem[] = [
      { label: "Dashboard", to: "/dashboard" },
      { label: "Productos", to: "/products" },
      { label: "Inventario", to: "/inventory" },
    ];
    if (user?.role === "admin" || user?.role === "vendedor") {
      baseItems.push({ label: "Clientes", to: "/customers" });
      baseItems.push({ label: "POS", to: "/pos" });
    }
    if (user?.role === "admin" || user?.role === "vendedor" || user?.role === "bodeguero") {
      baseItems.push({ label: "Ventas", to: "/sales" });
    }
    if (user?.role === "admin" || user?.role === "bodeguero") {
      baseItems.push({ label: "Compras", to: "/purchases" });
    }
    if (isAdmin) {
      baseItems.push({ label: "Categorías", to: "/categories" });
      baseItems.push({ label: "Proveedores", to: "/suppliers" });
    }
    return baseItems;
  }, [accessToken, isAdmin, user?.role]);

  if (!accessToken) {
    return <Outlet />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 border-r border-slate-300 bg-white p-5 dark:border-slate-700 dark:bg-slate-900 md:flex md:flex-col md:justify-between">
          <SidebarContent
            navItems={navItems}
            currentPath={location.pathname}
            userName={user?.full_name ?? "Usuario"}
            userRole={user?.role ?? "sin rol"}
            onLogout={() => {
              void logout();
            }}
          />
        </aside>

        <div className="flex-1">
          <header className="sticky top-0 z-30 border-b border-slate-300 bg-white/90 px-4 py-3 backdrop-blur dark:border-slate-700 dark:bg-slate-900/90 md:hidden">
            <div className="mx-auto flex max-w-6xl items-center justify-between">
              <h1 className="text-lg font-semibold">NexusERP</h1>
              <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                <SheetTrigger>
                  <Button type="button">Menú</Button>
                </SheetTrigger>
                <SheetContent>
                  <SidebarContent
                    navItems={navItems}
                    currentPath={location.pathname}
                    userName={user?.full_name ?? "Usuario"}
                    userRole={user?.role ?? "sin rol"}
                    onNavigate={() => setMobileOpen(false)}
                    onLogout={() => {
                      setMobileOpen(false);
                      void logout();
                    }}
                  />
                </SheetContent>
              </Sheet>
            </div>
          </header>

          <Outlet />
        </div>
      </div>
    </div>
  );
}

type SidebarContentProps = {
  navItems: NavItem[];
  currentPath: string;
  userName: string;
  userRole: string;
  onNavigate?: () => void;
  onLogout: () => void;
};

function SidebarContent({
  navItems,
  currentPath,
  userName,
  userRole,
  onNavigate,
  onLogout,
}: SidebarContentProps) {
  return (
    <>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">NexusERP</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">Panel operativo</p>
        </div>

        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const isActive = currentPath === item.to || currentPath.startsWith(`${item.to}/`);
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onNavigate}
                className={[
                  "rounded-md px-3 py-2 text-sm font-medium transition",
                  isActive
                    ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                    : "text-slate-700 hover:bg-slate-200 dark:text-slate-200 dark:hover:bg-slate-800",
                ].join(" ")}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="space-y-3 border-t border-slate-300 pt-4 dark:border-slate-700">
        <p className="text-sm text-slate-700 dark:text-slate-200">{userName}</p>
        <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Rol: {userRole}</p>
        <Button type="button" className="w-full" onClick={onLogout}>
          Cerrar sesión
        </Button>
      </div>
    </>
  );
}
