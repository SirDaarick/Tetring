/** Card de métrica para el dashboard.
 *
 * Muestra un número grande con su etiqueta, icono e indicador de tendencia.
 * El número se anima desde 0 hasta el valor final al montarse.
 */
import type { ReactElement } from "react";
import { memo, useEffect, useState } from "react";
import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";

interface MetricCardProps {
  icon: LucideIcon;
  value?: number | null;
  textValue?: string | null;
  label: string;
  subtitle?: string;
  decimals?: number;
  trend?: {
    value: string;
    label: string;
    isPositive: boolean;
  };
}

function useAnimatedNumber(
  target: number,
  decimals = 0,
  duration = 800
): number {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    let start: number | null = null;
    let raf: number;
    const factor = 10 ** decimals;

    function step(timestamp: number): void {
      if (start === null) {
        start = timestamp;
      }
      const progress = Math.min((timestamp - start) / duration, 1);
      const raw = target * progress;
      setCurrent(Math.round(raw * factor) / factor);
      if (progress < 1) {
        raf = requestAnimationFrame(step);
      }
    }

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, decimals, duration]);

  return current;
}

function formatMetric(value: number, decimals = 0): string {
  return decimals > 0
    ? value.toLocaleString("es-MX", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    : value.toLocaleString("es-MX");
}

export const MetricCard = memo(function MetricCard({
  icon: Icon,
  value,
  textValue,
  label,
  subtitle,
  decimals = 0,
  trend,
}: MetricCardProps): ReactElement {
  const animated = useAnimatedNumber(value ?? 0, decimals);
  const display =
    textValue !== undefined && textValue !== null
      ? textValue
      : value === null || value === undefined || Number.isNaN(value)
      ? "--"
      : formatMetric(animated, decimals);

  return (
    <Card className="rounded-clay-xl border-0 bg-white/75 p-4 shadow-clay backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg flex flex-col justify-between">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-clay-surface text-clay-primary shadow-clay-input shrink-0">
            <Icon className="h-4 w-4" />
          </div>
          <span className="text-xs font-semibold text-clay-text-secondary uppercase tracking-wider">
            {label}
          </span>
        </div>
        {trend ? (
          <span
            className={`text-[11px] font-medium ${
              trend.isPositive ? "text-clay-success" : "text-clay-error"
            }`}
          >
            {trend.value} {trend.label}
          </span>
        ) : null}
      </div>

      <div className="mt-2.5 flex items-baseline justify-between gap-2">
        <div className="text-2xl sm:text-3xl font-black text-clay-text tracking-tight">
          {display}
        </div>
        {subtitle ? (
          <div className="text-[11px] text-clay-text-secondary font-medium text-right line-clamp-1">
            {subtitle}
          </div>
        ) : null}
      </div>
    </Card>
  );
});
