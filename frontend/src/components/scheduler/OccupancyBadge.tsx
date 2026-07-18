/** Badge semáforo de disponibilidad de cupo.
 *
 * 🟢 Disponible, 🟡 Bajo, 🟠 Crítico, 🔴 Lleno.
 */
import type { ReactElement } from "react";

import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface OccupancyBadgeProps {
  available: number;
}

function getOccupancyMeta(available: number): {
  label: string;
  variant: "default" | "secondary" | "destructive" | "outline";
  className: string;
} {
  if (available >= 10) {
    return {
      label: "Disponible",
      variant: "outline",
      className: "border-emerald-500/50 bg-emerald-500/10 text-emerald-700",
    };
  }
  if (available >= 5) {
    return {
      label: "Bajo",
      variant: "outline",
      className: "border-amber-500/50 bg-amber-500/10 text-amber-700",
    };
  }
  if (available >= 1) {
    return {
      label: "Crítico",
      variant: "outline",
      className: "border-orange-500/50 bg-orange-500/10 text-orange-700",
    };
  }
  return {
    label: "Lleno",
    variant: "destructive",
    className: "border-red-500/50 bg-red-500/10 text-red-700",
  };
}

export function OccupancyBadge({ available }: OccupancyBadgeProps): ReactElement {
  const meta = getOccupancyMeta(available);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <Badge
            variant={meta.variant}
            className={`rounded-full ${meta.className}`}
          >
            {meta.label}
          </Badge>
        </TooltipTrigger>
        <TooltipContent
          side="top"
          className="rounded-lg bg-clay-text text-white"
        >
          {available} lugares disponibles
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
