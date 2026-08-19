import type { ReactElement } from "react";
import { Clock, Sun, Moon, Sparkles } from "lucide-react";

import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";

export type OrderCriterion = "compact" | "late" | "free";
export type TurnoFilter = "matutino" | "vespertino" | "mixto";
export type MaxResults = 50 | 100 | 200 | 500;

interface FilterPanelProps {
  criterion: OrderCriterion;
  onCriterionChange: (value: OrderCriterion) => void;
  turno: TurnoFilter;
  onTurnoChange: (value: TurnoFilter) => void;
  timeRange: [number, number];
  onTimeRangeChange: (value: [number, number]) => void;
  maxResults: MaxResults;
  onMaxResultsChange: (value: MaxResults) => void;
}

const CRITERIA: { value: OrderCriterion; label: string; desc: string }[] = [
  { value: "compact", label: "Menos huecos", desc: "Clases continuas y compactas" },
  { value: "late", label: "Entrar más tarde", desc: "Priorizar horario matutino tardío" },
  { value: "free", label: "Más días libres", desc: "Concentrar materias en menos días" },
];

const MAX_RESULTS_OPTIONS: MaxResults[] = [50, 100, 200, 500];

function formatHour(value: number): string {
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  const period = hours >= 12 ? "PM" : "AM";
  const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
  return `${displayHours}:${minutes.toString().padStart(2, "0")} ${period}`;
}

export function FilterPanel({
  criterion,
  onCriterionChange,
  turno,
  onTurnoChange,
  timeRange,
  onTimeRangeChange,
  maxResults,
  onMaxResultsChange,
}: FilterPanelProps): ReactElement {
  return (
    <div className="space-y-6 rounded-clay border-0 bg-white/70 p-5 shadow-clay backdrop-blur-md">
      {/* 1. Criterio de optimización */}
      <div className="space-y-3">
        <Label className="text-sm font-bold text-clay-text flex items-center gap-1.5">
          <Sparkles className="h-4 w-4 text-clay-primary" />
          Optimizar horario por
        </Label>
        <RadioGroup
          value={criterion}
          onValueChange={(value) => onCriterionChange(value as OrderCriterion)}
          className="gap-2"
        >
          {CRITERIA.map((item) => (
            <label
              key={item.value}
              htmlFor={`criterion-${item.value}`}
              className={`flex cursor-pointer items-start gap-3 rounded-2xl p-3 transition-all ${
                criterion === item.value
                  ? "bg-clay-surface border border-clay-primary/20 shadow-clay-input"
                  : "hover:bg-clay-surface/40"
              }`}
            >
              <RadioGroupItem
                value={item.value}
                id={`criterion-${item.value}`}
                className="mt-0.5 border-clay-border text-clay-primary"
              />
              <div className="flex flex-col">
                <span className="text-xs font-bold text-clay-text">{item.label}</span>
                <span className="text-[11px] text-clay-text-secondary">{item.desc}</span>
              </div>
            </label>
          ))}
        </RadioGroup>
      </div>

      {/* 2. Turno Escolar */}
      <div className="space-y-2.5">
        <Label htmlFor="turno-select" className="text-sm font-bold text-clay-text">
          Turno Preferente
        </Label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: "matutino", label: "Matutino", icon: Sun },
            { value: "vespertino", label: "Vespertino", icon: Moon },
            { value: "mixto", label: "Cualquiera", icon: Clock },
          ].map((t) => {
            const Icon = t.icon;
            const isSelected = turno === t.value;
            return (
              <button
                key={t.value}
                type="button"
                onClick={() => onTurnoChange(t.value as TurnoFilter)}
                className={`flex flex-col items-center justify-center gap-1 py-2.5 px-2 rounded-2xl text-xs font-bold transition-all ${
                  isSelected
                    ? "bg-white text-clay-primary shadow-clay border border-clay-primary/20"
                    : "bg-clay-surface/40 text-clay-text-secondary hover:text-clay-text hover:bg-clay-surface"
                }`}
              >
                <Icon className={`h-4 w-4 ${isSelected ? "text-clay-primary" : "text-clay-text-secondary"}`} />
                {t.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Selector Visual de Rango Horario */}
      <div className="space-y-3.5 pt-1">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-bold text-clay-text flex items-center gap-1.5">
            <Clock className="h-4 w-4 text-clay-primary" />
            Límites de Horario
          </Label>
        </div>

        {/* Tarjetas interactivas de hora inicio y fin */}
        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-2xl bg-clay-surface/60 p-2.5 text-center shadow-clay-pressed border border-clay-border/10">
            <span className="text-[10px] uppercase font-bold text-clay-text-secondary block mb-0.5">
              No antes de
            </span>
            <span className="text-sm font-mono font-bold text-clay-primary">
              {formatHour(timeRange[0])}
            </span>
          </div>
          <div className="rounded-2xl bg-clay-surface/60 p-2.5 text-center shadow-clay-pressed border border-clay-border/10">
            <span className="text-[10px] uppercase font-bold text-clay-text-secondary block mb-0.5">
              No después de
            </span>
            <span className="text-sm font-mono font-bold text-clay-primary">
              {formatHour(timeRange[1])}
            </span>
          </div>
        </div>

        <Slider
          value={timeRange}
          min={420} // 07:00 AM
          max={1320} // 10:00 PM
          step={30}
          onValueChange={(value) => onTimeRangeChange(value as [number, number])}
          className="py-3"
        />

        {/* Atajos rápidos de horario */}
        <div className="flex flex-wrap items-center justify-between gap-1 text-[10px] text-clay-text-secondary">
          <span>7:00 AM</span>
          <div className="flex gap-1.5">
            <button
              type="button"
              onClick={() => onTimeRangeChange([420, 900])} // 7:00 - 15:00
              className="px-2 py-0.5 rounded-lg bg-clay-surface/70 hover:bg-clay-surface font-medium hover:text-clay-primary transition-colors"
            >
              7AM - 3PM
            </button>
            <button
              type="button"
              onClick={() => onTimeRangeChange([840, 1320])} // 14:00 - 22:00
              className="px-2 py-0.5 rounded-lg bg-clay-surface/70 hover:bg-clay-surface font-medium hover:text-clay-primary transition-colors"
            >
              2PM - 10PM
            </button>
            <button
              type="button"
              onClick={() => onTimeRangeChange([420, 1320])} // Completo
              className="px-2 py-0.5 rounded-lg bg-clay-surface/70 hover:bg-clay-surface font-medium hover:text-clay-primary transition-colors"
            >
              Todo
            </button>
          </div>
          <span>10:00 PM</span>
        </div>
      </div>

      {/* 4. Límite de combinaciones */}
      <div className="space-y-2.5 pt-1 border-t border-clay-border/10">
        <Label htmlFor="max-results-select" className="text-xs font-semibold text-clay-text-secondary">
          Límite de combinaciones a generar
        </Label>
        <Select
          value={String(maxResults)}
          onValueChange={(value) => onMaxResultsChange(Number(value) as MaxResults)}
        >
          <SelectTrigger
            id="max-results-select"
            className="rounded-2xl border-0 bg-[#f4f1fa] shadow-clay-input focus:ring-2 focus:ring-clay-primary focus:ring-offset-2"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="rounded-clay border-0 bg-white/95 shadow-clay-lg backdrop-blur-md">
            {MAX_RESULTS_OPTIONS.map((option) => (
              <SelectItem key={option} value={String(option)}>
                Hasta {option} horarios
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
