import { Badge } from "../../../components/ui/badge";

import type { OrderStatusType } from "../types/purchases.types";

type OrderStatusBadgeProps = {
  status: OrderStatusType;
  className?: string;
};

const statusLabelMap: Record<OrderStatusType, string> = {
  draft: "Borrador",
  confirmed: "Confirmada",
  received: "Recibida",
  cancelled: "Cancelada",
};

const statusColorMap: Record<OrderStatusType, string> = {
  draft: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  confirmed: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  received: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export function OrderStatusBadge({ status, className }: OrderStatusBadgeProps) {
  return (
    <Badge className={`${statusColorMap[status]} ${className ?? ""}`.trim()}>
      {statusLabelMap[status]}
    </Badge>
  );
}
