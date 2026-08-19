import type { ReactElement } from "react";
import { memo, useMemo, useState } from "react";
import {
  Save,
  Star,
  LayoutGrid,
  Table as TableIcon,
  Clock,
  User,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { OccupancyBadge } from "@/components/scheduler/OccupancyBadge";

export interface ScheduleGroup {
  grupo: string;
  asignatura: string;
  profesor: string;
  horario: string;
  cupo: number;
  disponibles?: number;
  lunes?: string | null;
  martes?: string | null;
  miercoles?: string | null;
  jueves?: string | null;
  viernes?: string | null;
}

export interface ScheduleResult {
  id: string;
  rank: number;
  label: string;
  freeHours: number;
  groups: ScheduleGroup[];
}

interface ScheduleCardProps {
  schedule: ScheduleResult;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
  onSave?: () => void;
}

export { Accordion };

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"];
const HORA_INICIO = 7;
const HORA_FIN = 22;
const TOTAL_HORAS = HORA_FIN - HORA_INICIO;

const PALETA_COLORES = [
  {
    bg: "bg-indigo-500/15 hover:bg-indigo-500/25",
    border: "border-indigo-500/40",
    badge: "bg-indigo-600 text-white",
  },
  {
    bg: "bg-emerald-500/15 hover:bg-emerald-500/25",
    border: "border-emerald-500/40",
    badge: "bg-emerald-600 text-white",
  },
  {
    bg: "bg-amber-500/15 hover:bg-amber-500/25",
    border: "border-amber-500/40",
    badge: "bg-amber-600 text-white",
  },
  {
    bg: "bg-purple-500/15 hover:bg-purple-500/25",
    border: "border-purple-500/40",
    badge: "bg-purple-600 text-white",
  },
  {
    bg: "bg-sky-500/15 hover:bg-sky-500/25",
    border: "border-sky-500/40",
    badge: "bg-sky-600 text-white",
  },
  {
    bg: "bg-rose-500/15 hover:bg-rose-500/25",
    border: "border-rose-500/40",
    badge: "bg-rose-600 text-white",
  },
  {
    bg: "bg-teal-500/15 hover:bg-teal-500/25",
    border: "border-teal-500/40",
    badge: "bg-teal-600 text-white",
  },
  {
    bg: "bg-orange-500/15 hover:bg-orange-500/25",
    border: "border-orange-500/40",
    badge: "bg-orange-600 text-white",
  },
];

function abreviarMateria(nombre: string): string {
  if (!nombre) return "";
  const palabras = nombre.trim().split(/\s+/);
  if (palabras.length <= 2) return nombre;

  const descartar = new Set([
    "DE", "DEL", "LA", "LAS", "EL", "LOS", "EN", "Y", "E", "A", "PARA", "POR", "CON"
  ]);

  const significativas = palabras.filter(p => !descartar.has(p.toUpperCase()));
  if (significativas.length <= 3) {
    return significativas.join(" ");
  }

  return significativas
    .slice(0, 3)
    .map(p => (p.length > 3 ? p.slice(0, 4) + "." : p))
    .join(" ");
}

interface ClassBlock {
  id: string;
  grupo: string;
  asignatura: string;
  profesor: string;
  cupo: number;
  disponibles?: number;
  dayIndex: number;
  startHour: number;
  startMinute: number;
  endHour: number;
  endMinute: number;
  durationMinutes: number;
  colorClass: (typeof PALETA_COLORES)[0];
}

function parseTimeRange(timeStr: string): { startH: number; startM: number; endH: number; endM: number; duration: number } | null {
  if (!timeStr) return null;
  const match = timeStr.match(/(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})/);
  if (!match) return null;

  const startH = parseInt(match[1], 10);
  const startM = parseInt(match[2], 10);
  const endH = parseInt(match[3], 10);
  const endM = parseInt(match[4], 10);
  const duration = (endH * 60 + endM) - (startH * 60 + startM);
  if (duration <= 0) return null;

  return { startH, startM, endH, endM, duration };
}

function parseScheduleToBlocks(
  groups: ScheduleGroup[],
  colorsMap: Map<string, (typeof PALETA_COLORES)[0]>
): ClassBlock[] {
  const blocks: ClassBlock[] = [];
  const DIAS_KEYS: Array<{ key: keyof ScheduleGroup; dayIndex: number; name: string }> = [
    { key: "lunes", dayIndex: 0, name: "Lun" },
    { key: "martes", dayIndex: 1, name: "Mar" },
    { key: "miercoles", dayIndex: 2, name: "Mie" },
    { key: "jueves", dayIndex: 3, name: "Jue" },
    { key: "viernes", dayIndex: 4, name: "Vie" },
  ];

  groups.forEach((group, idx) => {
    const color = colorsMap.get(group.asignatura) || PALETA_COLORES[idx % PALETA_COLORES.length];

    // Intentar primero parsear por propiedades individuales de día
    let matchedAnyDay = false;
    for (const d of DIAS_KEYS) {
      const val = group[d.key];
      if (typeof val === "string" && val.trim()) {
        const parsed = parseTimeRange(val);
        if (parsed) {
          matchedAnyDay = true;
          blocks.push({
            id: `${group.grupo}-${group.asignatura}-${d.dayIndex}-${parsed.startH}-${parsed.startM}`,
            grupo: group.grupo,
            asignatura: group.asignatura,
            profesor: group.profesor,
            cupo: group.cupo,
            disponibles: group.disponibles,
            dayIndex: d.dayIndex,
            startHour: parsed.startH,
            startMinute: parsed.startM,
            endHour: parsed.endH,
            endMinute: parsed.endM,
            durationMinutes: parsed.duration,
            colorClass: color,
          });
        }
      }
    }

    // Fallback: parsear string combinado de group.horario si no venían las keys individuales
    if (!matchedAnyDay && group.horario) {
      const DIAS_MAP: Record<string, number> = {
        LUN: 0, LUNES: 0, MAR: 1, MARTES: 1, MIE: 2, MIER: 2, MIERCOLES: 2, MIÉRCOLES: 2, JUE: 3, JUEVES: 3, VIE: 4, VIERNES: 4,
      };
      const regex = /(LUNES|MARTES|MI[EÉ]RCOLES|JUEVES|VIERNES|LUN|MAR|MIE|MIER|JUE|VIE)[:\s]+(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})/gi;
      let match;

      while ((match = regex.exec(group.horario)) !== null) {
        const dayStr = match[1].toUpperCase();
        const dayIndex = DIAS_MAP[dayStr];
        if (dayIndex === undefined) continue;

        const startH = parseInt(match[2], 10);
        const startM = parseInt(match[3], 10);
        const endH = parseInt(match[4], 10);
        const endM = parseInt(match[5], 10);
        const duration = (endH * 60 + endM) - (startH * 60 + startM);

        blocks.push({
          id: `${group.grupo}-${group.asignatura}-${dayIndex}-${startH}-${startM}`,
          grupo: group.grupo,
          asignatura: group.asignatura,
          profesor: group.profesor,
          cupo: group.cupo,
          disponibles: group.disponibles,
          dayIndex,
          startHour: startH,
          startMinute: startM,
          endHour: endH,
          endMinute: endM,
          durationMinutes: duration,
          colorClass: color,
        });
      }
    }
  });

  return blocks;
}

function ScheduleVisualGrid({ groups }: { groups: ScheduleGroup[] }): ReactElement {
  const colorsMap = useMemo(() => {
    const map = new Map<string, (typeof PALETA_COLORES)[0]>();
    const asignaturasUnicas = Array.from(new Set(groups.map((g) => g.asignatura)));
    asignaturasUnicas.forEach((asig, i) => {
      map.set(asig, PALETA_COLORES[i % PALETA_COLORES.length]);
    });
    return map;
  }, [groups]);

  const blocks = useMemo(() => parseScheduleToBlocks(groups, colorsMap), [groups, colorsMap]);

  const hours = useMemo(() => {
    const list: number[] = [];
    for (let h = HORA_INICIO; h <= HORA_FIN; h++) {
      list.push(h);
    }
    return list;
  }, []);

  const ROW_HEIGHT_PX = 42;

  return (
    <TooltipProvider delay={80}>
      <div className="w-full overflow-x-auto rounded-2xl bg-white/40 p-2 sm:p-4 backdrop-blur-sm border border-clay-border/20">
        <div className="min-w-[620px]">
          {/* Encabezado con los días */}
          <div className="grid grid-cols-[50px_repeat(5,1fr)] gap-1.5 border-b border-clay-border/20 pb-2 text-center">
            <span className="text-[11px] font-semibold text-clay-text-secondary">Hora</span>
            {DIAS.map((dia) => (
              <span key={dia} className="text-xs font-bold text-clay-text uppercase tracking-wider">
                {dia}
              </span>
            ))}
          </div>

          {/* Cuadrícula de Horarios */}
          <div className="relative mt-2 grid grid-cols-[50px_repeat(5,1fr)] gap-1.5">
            {/* Columna de Horas */}
            <div
              className="flex flex-col text-right pr-2 select-none"
              style={{ height: `${TOTAL_HORAS * ROW_HEIGHT_PX}px` }}
            >
              {hours.map((h) => (
                <div
                  key={h}
                  className="text-[10px] font-mono text-clay-text-secondary/70 -translate-y-2"
                  style={{ height: `${ROW_HEIGHT_PX}px` }}
                >
                  {String(h).padStart(2, "0")}:00
                </div>
              ))}
            </div>

            {/* 5 Columnas de Días */}
            {DIAS.map((dia, dayIndex) => {
              const dayBlocks = blocks.filter((b) => b.dayIndex === dayIndex);

              return (
                <div
                  key={dia}
                  className="relative rounded-xl bg-clay-surface/20 border border-clay-border/10 overflow-hidden"
                  style={{ height: `${TOTAL_HORAS * ROW_HEIGHT_PX}px` }}
                >
                  {/* Líneas divisorias de cada hora */}
                  {hours.map((h, i) => (
                    <div
                      key={h}
                      className="border-t border-dashed border-clay-border/15 absolute left-0 right-0"
                      style={{ top: `${i * ROW_HEIGHT_PX}px` }}
                    />
                  ))}

                  {/* Bloques de clase */}
                  {dayBlocks.map((block) => {
                    const topOffsetMinutes = (block.startHour - HORA_INICIO) * 60 + block.startMinute;
                    const topPx = (topOffsetMinutes / 60) * ROW_HEIGHT_PX;
                    const heightPx = (block.durationMinutes / 60) * ROW_HEIGHT_PX - 2;

                    const timeStr = `${String(block.startHour).padStart(2, "0")}:${String(block.startMinute).padStart(2, "0")} - ${String(block.endHour).padStart(2, "0")}:${String(block.endMinute).padStart(2, "0")}`;

                    return (
                      <Tooltip key={block.id}>
                        <TooltipTrigger asChild>
                          <div
                            tabIndex={0}
                            role="button"
                            className={`absolute left-0.5 right-0.5 rounded-lg border p-1.5 shadow-sm transition-all duration-200 cursor-pointer flex flex-col justify-between overflow-hidden z-10 ${block.colorClass.bg} ${block.colorClass.border} hover:z-30 hover:scale-[1.02] hover:shadow-md focus:outline-none focus:ring-2 focus:ring-clay-primary`}
                            style={{
                              top: `${topPx}px`,
                              height: `${Math.max(heightPx, 32)}px`,
                            }}
                          >
                            <div className="space-y-0.5 min-w-0">
                              <div className="flex items-center justify-between gap-1">
                                <span className="font-bold text-[11px] leading-tight line-clamp-1 text-clay-text">
                                  {abreviarMateria(block.asignatura)}
                                </span>
                                <span className={`text-[9px] font-mono px-1 py-0.2 rounded font-bold shrink-0 ${block.colorClass.badge}`}>
                                  {block.grupo}
                                </span>
                              </div>
                              {block.profesor ? (
                                <p className="text-[10px] text-clay-text/80 font-medium truncate leading-none">
                                  {block.profesor}
                                </p>
                              ) : null}
                            </div>
                            <div className="text-[9.5px] text-clay-text-secondary/90 font-mono mt-0.5">
                              {timeStr}
                            </div>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent
                          side="top"
                          align="center"
                          className="w-72 p-3.5 rounded-2xl bg-white text-clay-text shadow-clay-lg backdrop-blur-md border border-clay-border/40 z-50 animate-scale-in"
                        >
                          <div className="space-y-2 text-xs">
                            <div className="border-b border-clay-border/20 pb-1.5">
                              <div className="flex items-center justify-between gap-2">
                                <span className="font-bold text-sm text-clay-text">
                                  {block.asignatura}
                                </span>
                                <span className="rounded-md bg-clay-primary px-1.5 py-0.5 font-mono text-[11px] font-bold text-white">
                                  {block.grupo}
                                </span>
                              </div>
                            </div>

                            <div className="space-y-1.5 text-clay-text-secondary">
                              <div className="flex items-center gap-2">
                                <Clock className="h-3.5 w-3.5 text-clay-primary shrink-0" />
                                <span className="font-mono text-[11px]">
                                  {DIAS[block.dayIndex]}: {timeStr}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <User className="h-3.5 w-3.5 text-clay-primary shrink-0" />
                                <span className="truncate">
                                  {block.profesor || "Sin profesor asignado"}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Users className="h-3.5 w-3.5 text-clay-primary shrink-0" />
                                <span>
                                  Cupo: <strong className="text-clay-text">{block.disponibles ?? block.cupo}</strong> disp / {block.cupo}
                                </span>
                              </div>
                            </div>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

export const ScheduleCard = memo(function ScheduleCard({
  schedule,
  isFavorite,
  onToggleFavorite,
  onSave,
}: ScheduleCardProps): ReactElement {
  const [viewMode, setViewMode] = useState<"visual" | "table">("visual");

  return (
    <AccordionItem
      value={schedule.id}
      className="overflow-hidden rounded-clay-lg border-0 bg-white/70 shadow-clay backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-clay-lg"
    >
      <AccordionTrigger className="px-5 py-4 text-left text-clay-text hover:no-underline">
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-clay-primary-soft to-clay-primary text-sm font-bold text-white">
            #{schedule.rank}
          </span>
          <div>
            <h3 className="font-semibold text-clay-text">{schedule.label}</h3>
            <p className="text-xs text-clay-text-secondary">
              {schedule.freeHours.toFixed(1)} hrs libres
            </p>
          </div>
        </div>
      </AccordionTrigger>
      <AccordionContent className="px-5 pb-4">
        {/* Toggle de Modo de Vista */}
        <div className="mb-3 flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-clay-text-secondary">
            {viewMode === "visual" ? "Vista de Horario Semanal" : "Detalle en Tabla"}
          </span>
          <div className="inline-flex rounded-xl bg-clay-surface p-1 shadow-inner">
            <button
              type="button"
              onClick={() => setViewMode("visual")}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                viewMode === "visual"
                  ? "bg-white text-clay-primary shadow-clay"
                  : "text-clay-text-secondary hover:text-clay-text"
              }`}
            >
              <LayoutGrid className="h-3.5 w-3.5" />
              Bloques
            </button>
            <button
              type="button"
              onClick={() => setViewMode("table")}
              className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                viewMode === "table"
                  ? "bg-white text-clay-primary shadow-clay"
                  : "text-clay-text-secondary hover:text-clay-text"
              }`}
            >
              <TableIcon className="h-3.5 w-3.5" />
              Tabla
            </button>
          </div>
        </div>

        {/* Renderizado condicional: Bloques Visuales o Tabla */}
        {viewMode === "visual" ? (
          <ScheduleVisualGrid groups={schedule.groups} />
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-clay-border hover:bg-transparent">
                  <TableHead className="text-clay-text">Gru</TableHead>
                  <TableHead className="text-clay-text">Asignatura</TableHead>
                  <TableHead className="text-clay-text">Prof</TableHead>
                  <TableHead className="text-clay-text">Horario</TableHead>
                  <TableHead className="text-clay-text">Cupo</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {schedule.groups.map((group) => (
                  <TableRow
                    key={group.grupo + group.asignatura}
                    className="border-clay-border hover:bg-clay-surface/50"
                  >
                    <TableCell className="font-mono text-sm text-clay-text">
                      {group.grupo}
                    </TableCell>
                    <TableCell className="text-clay-text">
                      {group.asignatura}
                    </TableCell>
                    <TableCell className="text-clay-text-secondary">
                      {group.profesor}
                    </TableCell>
                    <TableCell className="font-mono text-sm text-clay-text-secondary">
                      {group.horario}
                    </TableCell>
                    <TableCell>
                      <OccupancyBadge
                        disponibles={group.disponibles ?? group.cupo}
                        cupo={group.cupo}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}

        <div className="mt-4 flex items-center justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onToggleFavorite}
            className="gap-2 rounded-clay border-clay-border bg-white/70 text-clay-text shadow-clay transition-all hover:-translate-y-0.5 hover:bg-white hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
          >
            <Star
              className={`h-4 w-4 ${
                isFavorite ? "fill-amber-400 text-amber-400" : "text-clay-text-secondary"
              }`}
            />
            {isFavorite ? "Favorito" : "Favorito"}
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onSave}
            className="gap-2 rounded-clay border-clay-border bg-white/70 text-clay-text shadow-clay transition-all hover:-translate-y-0.5 hover:bg-white hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
          >
            <Save className="h-4 w-4" />
            Guardar
          </Button>
        </div>
      </AccordionContent>
    </AccordionItem>
  );
});
