import * as React from "react";

import { cn } from "../../lib/utils";

type SeparatorProps = React.HTMLAttributes<HTMLDivElement>;

export function Separator({ className, ...props }: SeparatorProps) {
  return <div className={cn("h-px w-full bg-slate-200 dark:bg-slate-700", className)} {...props} />;
}
