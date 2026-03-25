import * as React from "react";

import { cn } from "../../lib/utils";

type SheetContextValue = {
  open: boolean;
  onOpenChange: (next: boolean) => void;
};

const SheetContext = React.createContext<SheetContextValue | null>(null);

function useSheetContext() {
  const context = React.useContext(SheetContext);
  if (!context) {
    throw new Error("Sheet components must be used inside <Sheet>");
  }
  return context;
}

type SheetProps = {
  open: boolean;
  onOpenChange: (next: boolean) => void;
  children: React.ReactNode;
};

export function Sheet({ open, onOpenChange, children }: SheetProps) {
  return <SheetContext.Provider value={{ open, onOpenChange }}>{children}</SheetContext.Provider>;
}

type SheetTriggerProps = {
  children: React.ReactElement;
};

export function SheetTrigger({ children }: SheetTriggerProps) {
  const { onOpenChange } = useSheetContext();
  return React.cloneElement(children, {
    onClick: () => onOpenChange(true),
  });
}

export function SheetContent({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  const { open, onOpenChange } = useSheetContext();
  if (!open) {
    return null;
  }
  return (
    <div className="fixed inset-0 z-50 md:hidden">
      <button
        type="button"
        aria-label="Cerrar menú"
        className="absolute inset-0 bg-slate-900/50"
        onClick={() => onOpenChange(false)}
      />
      <aside
        className={cn(
          "absolute left-0 top-0 h-full w-72 border-r border-slate-300 bg-white p-4 shadow-xl dark:border-slate-700 dark:bg-slate-900",
          className
        )}
      >
        {children}
      </aside>
    </div>
  );
}
