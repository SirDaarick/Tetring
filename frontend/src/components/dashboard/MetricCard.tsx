/** Card de métrica para el dashboard.
 *
 * Muestra un número grande con su etiqueta debajo.
 */
import type { ReactElement } from "react";

import { Card } from "@/components/ui/card";

interface MetricCardProps {
  value: string | number;
  label: string;
}

export function MetricCard({ value, label }: MetricCardProps): ReactElement {
  return (
    <Card className="rounded-clay-lg border-0 bg-white/70 p-6 shadow-clay backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-clay-lg">
      <div className="text-3xl font-bold text-clay-text">{value}</div>
      <div className="mt-1 text-sm text-clay-text-secondary">{label}</div>
    </Card>
  );
}
