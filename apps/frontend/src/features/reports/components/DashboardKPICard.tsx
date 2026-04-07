import type { LucideIcon } from "lucide-react";

import { Badge } from "../../../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";

type DashboardKPICardProps = {
  label: string;
  value: number;
  unit?: "currency" | "number";
  icon: LucideIcon;
  trend?: number;
};

function formatValue(value: number, unit: "currency" | "number") {
  if (unit === "currency") {
    return new Intl.NumberFormat("es-EC", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(value);
  }

  return new Intl.NumberFormat("es-EC").format(value);
}

export function DashboardKPICard({ label, value, unit = "number", icon: Icon, trend }: DashboardKPICardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-slate-600 dark:text-slate-300">{label}</CardTitle>
        <Icon className="h-5 w-5 text-slate-500 dark:text-slate-300" />
      </CardHeader>
      <CardContent className="flex items-end justify-between">
        <p className="text-2xl font-semibold">{formatValue(value, unit)}</p>
        {trend !== undefined ? (
          <Badge className={trend >= 0 ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}>
            {trend >= 0 ? "▲" : "▼"} {Math.abs(trend).toFixed(1)}%
          </Badge>
        ) : null}
      </CardContent>
    </Card>
  );
}
