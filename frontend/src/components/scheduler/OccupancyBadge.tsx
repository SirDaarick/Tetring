/** Badge semáforo de disponibilidad de cupo.
 *
 * 🟢 Disponible, 🟡 Bajo, 🟠 Crítico, 🔴 Lleno. El color comunica el estado
 * de inmediato; el tooltip muestra el número exacto.
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
  disponibles: number;
  cupo: number;
}

function getOccupancyMeta(
  disponibles: number
): {
  label: string;
  dotClass: string;
  className: string;
} {
  if (disponibles >= 10) {
    return {
      label: "Disponible",
      dotClass: "bg-emerald-500",
      className:
        "border-emerald-500/30 bg-emerald-500/10 text-emerald-700",
    };
  }
  if (disponibles >= 5) {
    return {
      label: "Bajo",
      dotClass: "bg-amber-500",
      className:
        "border-amber-500/30 bg-amber-500/10 text-amber-700",
    };
  }
  if (disponibles >= 1) {
    return {
      label: "Crítico",
      dotClass: "bg-orange-500",
      className:
        "border-orange-500/30 bg-orange-500/10 text-orange-700",
    };
  }
  return {
    label: "Lleno",
    dotClass: "bg-red-500",
    className:
      "border-red-500/30 bg-red-500/10 text-red-700",
  };
}

export function OccupancyBadge({
  disponibles,
  cupo,
}: OccupancyBadgeProps): ReactElement {
  const meta = getOccupancyMeta(disponibles);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <Badge
            variant="outline"
            className={`gap-1.5 rounded-full border ${meta.className}`}
          >
            <span className={`h-2 w-2 rounded-full ${meta.dotClass}`} />
            {meta.label}
          </Badge>
        </TooltipTrigger>
        <TooltipContent
          side="top"
          className="rounded-lg bg-clay-text text-white"
        >
          {disponibles} disponibles / {cupo} cupo
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
