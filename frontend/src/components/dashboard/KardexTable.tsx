import type { ReactElement } from "react";
import { useMemo, useState } from "react";
import { GraduationCap, TrendingUp, Award } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export interface KardexEntry {
  clave: string;
  asignatura: string;
  calificacion: number;
  periodo: string;
}

interface KardexTableProps {
  entries: KardexEntry[];
  isLoading?: boolean;
}

interface PeriodPerformance {
  periodo: string;
  semestreNum: number;
  average: number;
  count: number;
  accumulatedAverage: number;
}

export function PerformanceChart({ entries }: { entries: KardexEntry[] }): ReactElement | null {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const performanceData: PeriodPerformance[] = useMemo(() => {
    const map = new Map<string, KardexEntry[]>();
    entries.forEach((entry) => {
      const per = entry.periodo || "Sin periodo";
      if (!map.has(per)) {
        map.set(per, []);
      }
      map.get(per)!.push(entry);
    });

    const sorted = Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
    let totalScore = 0;
    let totalCount = 0;

    const list: PeriodPerformance[] = [];
    sorted.forEach(([periodo, items], idx) => {
      const validGrades = items
        .map((i) => (typeof i.calificacion === "number" ? i.calificacion : parseFloat(String(i.calificacion))))
        .filter((g) => !isNaN(g));

      if (validGrades.length === 0) return;

      const sum = validGrades.reduce((a, b) => a + b, 0);
      const avg = Number((sum / validGrades.length).toFixed(2));

      totalScore += sum;
      totalCount += validGrades.length;
      const accAvg = Number((totalScore / totalCount).toFixed(2));

      list.push({
        periodo,
        semestreNum: idx + 1,
        average: avg,
        count: items.length,
        accumulatedAverage: accAvg,
      });
    });

    return list;
  }, [entries]);

  if (performanceData.length < 1) return null;

  // Dimensiones del gráfico SVG
  const width = 680;
  const height = 180;
  const paddingX = 45;
  const paddingY = 30;

  const minGrade = 6.0;
  const maxGrade = 10.0;

  const points = performanceData.map((d, i) => {
    const x =
      performanceData.length === 1
        ? width / 2
        : paddingX + (i / (performanceData.length - 1)) * (width - 2 * paddingX);
    const y =
      height - paddingY - ((d.average - minGrade) / (maxGrade - minGrade)) * (height - 2 * paddingY);
    return { ...d, x, y };
  });

  const linePath =
    points.length === 1
      ? `M ${points[0].x - 30} ${points[0].y} L ${points[0].x + 30} ${points[0].y}`
      : points.reduce((acc, p, i) => `${acc} ${i === 0 ? "M" : "L"} ${p.x} ${p.y}`, "");

  const areaPath =
    points.length === 1
      ? ""
      : `${linePath} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${
          height - paddingY
        } Z`;

  const bestPeriod = [...performanceData].sort((a, b) => b.average - a.average)[0];

  return (
    <div className="rounded-clay-xl border-0 bg-white/75 p-5 shadow-clay backdrop-blur-md transition-all duration-300 hover:shadow-clay-lg mb-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-2 border-b border-clay-border/15">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 text-white shadow-sm">
            <TrendingUp className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-clay-text text-sm sm:text-base">
              Evolución del Rendimiento Académico
            </h3>
            <p className="text-xs text-clay-text-secondary">
              Promedio por semestre vs. promedio acumulado
            </p>
          </div>
        </div>

        {bestPeriod ? (
          <div className="flex items-center gap-2 rounded-xl bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-700 dark:text-amber-300">
            <Award className="h-4 w-4 text-amber-500" />
            <span>
              Mejor Semestre: <strong>{bestPeriod.semestreNum}.º ({bestPeriod.average})</strong>
            </span>
          </div>
        ) : null}
      </div>

      <div className="relative w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-44 select-none overflow-visible"
        >
          <defs>
            <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Líneas Guía de Calificación (6.0, 7.0, 8.0, 9.0, 10.0) */}
          {[6.0, 7.0, 8.0, 9.0, 10.0].map((val) => {
            const y = height - paddingY - ((val - minGrade) / (maxGrade - minGrade)) * (height - 2 * paddingY);
            return (
              <g key={val}>
                <line
                  x1={paddingX - 10}
                  y1={y}
                  x2={width - paddingX + 10}
                  y2={y}
                  stroke="currentColor"
                  strokeDasharray="4 4"
                  className="text-clay-border/30"
                  strokeWidth="1"
                />
                <text
                  x={paddingX - 16}
                  y={y + 3.5}
                  textAnchor="end"
                  className="text-[10px] fill-clay-text-secondary/70 font-mono font-medium"
                >
                  {val.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Área sombreada bajo la curva */}
          {areaPath ? <path d={areaPath} fill="url(#performanceGradient)" /> : null}

          {/* Línea principal del promedio semestral */}
          <path
            d={linePath}
            fill="none"
            stroke="#6366f1"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="drop-shadow-sm"
          />

          {/* Nodos de cada Semestre */}
          {points.map((p, idx) => {
            const isHovered = hoveredIdx === idx;
            return (
              <g
                key={p.periodo}
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                {/* Círculo exterior interactivo */}
                <circle
                  cx={p.x}
                  cy={p.y}
                  r={isHovered ? "8" : "5"}
                  className="fill-white stroke-indigo-600 transition-all duration-200"
                  strokeWidth="2.5"
                />

                {/* Valor numérico flotante sobre el punto */}
                <text
                  x={p.x}
                  y={p.y - 10}
                  textAnchor="middle"
                  className={`text-[11px] font-mono font-bold transition-all duration-200 ${
                    isHovered ? "fill-indigo-600 font-extrabold text-[12px]" : "fill-clay-text font-semibold"
                  }`}
                >
                  {p.average.toFixed(1)}
                </text>

                {/* Etiqueta del Semestre en el eje X */}
                <text
                  x={p.x}
                  y={height - 8}
                  textAnchor="middle"
                  className="text-[11px] fill-clay-text-secondary font-semibold"
                >
                  {p.semestreNum}° Sem
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Detalle activo al interactuar */}
      {hoveredIdx !== null && performanceData[hoveredIdx] ? (
        <div className="mt-2 flex items-center justify-center gap-4 text-xs text-clay-text bg-clay-surface/50 py-1.5 px-3 rounded-lg animate-fade-in">
          <span>
            <strong>{performanceData[hoveredIdx].semestreNum}.º Semestre</strong> (Periodo {performanceData[hoveredIdx].periodo})
          </span>
          <span>•</span>
          <span>Promedio Semestral: <strong className="text-indigo-600 font-mono">{performanceData[hoveredIdx].average}</strong></span>
          <span>•</span>
          <span>Promedio Acumulado: <strong className="text-clay-text font-mono">{performanceData[hoveredIdx].accumulatedAverage}</strong></span>
        </div>
      ) : null}
    </div>
  );
}

function TableSkeleton(): ReactElement {
  return (
    <div className="space-y-3 p-5">
      {Array.from({ length: 4 }).map((_, index) => (
        <Skeleton
          key={index}
          className="h-10 w-full rounded-clay-sm"
        />
      ))}
    </div>
  );
}

export function KardexTable({
  entries,
  isLoading,
}: KardexTableProps): ReactElement {
  // Agrupar entradas por periodo/semestre
  const groupedEntries = useMemo(() => {
    const map = new Map<string, KardexEntry[]>();
    entries.forEach((entry) => {
      const per = entry.periodo || "Periodo sin especificar";
      if (!map.has(per)) {
        map.set(per, []);
      }
      map.get(per)!.push(entry);
    });

    // Ordenar periodos cronológicamente y asignar número de semestre
    const sorted = Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));

    return sorted.map(([periodo, items], idx) => {
      const validGrades = items
        .map((i) => (typeof i.calificacion === "number" ? i.calificacion : parseFloat(String(i.calificacion))))
        .filter((g) => !isNaN(g));
      const avg =
        validGrades.length > 0
          ? (validGrades.reduce((a, b) => a + b, 0) / validGrades.length).toFixed(1)
          : null;

      return {
        periodo,
        semestreNum: idx + 1,
        items,
        average: avg,
        count: items.length,
      };
    });
  }, [entries]);

  if (isLoading) {
    return (
      <div className="rounded-clay-lg bg-white/70 shadow-clay backdrop-blur-md p-4">
        <TableSkeleton />
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="rounded-clay-lg bg-white/70 shadow-clay backdrop-blur-md p-8 text-center text-clay-text-secondary">
        Sin datos de kárdex. Sincroniza tu cuenta del SAES.
      </div>
    );
  }

  // Si solo hay un periodo o pocos, podemos abrir por defecto todos
  const defaultOpen = groupedEntries.map((g) => g.periodo);

  return (
    <Accordion
      multiple
      defaultValue={defaultOpen}
      className="space-y-4"
    >
      {groupedEntries.map((group) => (
        <AccordionItem
          key={group.periodo}
          value={group.periodo}
          className="overflow-hidden rounded-clay-xl border-0 bg-white/70 shadow-clay backdrop-blur-md transition-all duration-300 hover:shadow-clay-lg"
        >
          <AccordionTrigger className="px-5 py-3.5 text-left text-clay-text hover:no-underline hover:bg-clay-surface/30">
            <div className="flex flex-wrap items-center justify-between gap-3 w-full pr-3">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-clay-primary-soft to-clay-primary text-white font-bold text-xs shadow-sm">
                  {group.semestreNum}°
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-clay-text text-sm sm:text-base">
                      {group.semestreNum}.º Semestre
                    </h3>
                    <span className="rounded-md bg-clay-surface px-1.5 py-0.5 font-mono text-[11px] font-semibold text-clay-text-secondary">
                      Periodo {group.periodo}
                    </span>
                  </div>
                  <p className="text-xs text-clay-text-secondary">
                    {group.count} {group.count === 1 ? "materia cursada" : "materias cursadas"}
                  </p>
                </div>
              </div>

              {group.average !== null ? (
                <div className="flex items-center gap-1.5 rounded-lg bg-clay-surface/80 px-2.5 py-1 text-xs font-semibold text-clay-text">
                  <GraduationCap className="h-3.5 w-3.5 text-clay-primary" />
                  <span>Promedio: <strong className="text-clay-primary font-mono">{group.average}</strong></span>
                </div>
              ) : null}
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-5 pb-4 pt-1">
            <div className="overflow-x-auto rounded-xl border border-clay-border/20 bg-white/40">
              <Table>
                <TableHeader>
                  <TableRow className="border-clay-border/20 bg-clay-surface/30 hover:bg-transparent">
                    <TableHead className="text-clay-text font-bold text-xs">Clave</TableHead>
                    <TableHead className="text-clay-text font-bold text-xs">Asignatura</TableHead>
                    <TableHead className="text-clay-text font-bold text-xs text-right">Calificación</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {group.items.map((entry) => {
                    const numCalif = typeof entry.calificacion === "number" ? entry.calificacion : parseFloat(String(entry.calificacion));
                    const isApproved = !isNaN(numCalif) ? numCalif >= 6.0 : String(entry.calificacion).toUpperCase() === "AC";

                    return (
                      <TableRow
                        key={entry.clave + entry.periodo}
                        className="border-clay-border/10 transition-colors hover:bg-clay-surface/40"
                      >
                        <TableCell className="font-mono text-xs text-clay-text-secondary w-28">
                          {entry.clave}
                        </TableCell>
                        <TableCell className="font-medium text-sm text-clay-text">
                          {entry.asignatura}
                        </TableCell>
                        <TableCell className="text-right w-32">
                          <span
                            className={`inline-block font-mono text-xs font-bold px-2 py-0.5 rounded-md ${
                              isApproved
                                ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                                : "bg-rose-500/10 text-rose-700 dark:text-rose-300"
                            }`}
                          >
                            {entry.calificacion}
                          </span>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
