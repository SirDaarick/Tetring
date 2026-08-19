/** Panel de filtros del generador de horarios.
 *
 * Incluye criterio de orden, turno, rango horario, límite de resultados y
 * botón de generación con estado de carga.
 */
import type { ReactElement } from "react";

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
import { MultiSelect } from "@/components/ui/multi-select";

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
  availableProfessors?: string[];
  excludeProfessors?: string[];
  onExcludeProfessorsChange?: (value: string[]) => void;
}

const CRITERIA: { value: OrderCriterion; label: string }[] = [
  { value: "compact", label: "Compacto" },
  { value: "late", label: "Entrar tarde" },
  { value: "free", label: "Más días libres" },
];

const MAX_RESULTS_OPTIONS: MaxResults[] = [50, 100, 200, 500];

function formatHour(value: number): string {
  const hours = Math.floor(value / 60);
  const minutes = value % 60;
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
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
  availableProfessors = [],
  excludeProfessors = [],
  onExcludeProfessorsChange,
}: FilterPanelProps): ReactElement {
  return (
    <div className="space-y-6 rounded-clay border-0 bg-white/70 p-5 shadow-clay backdrop-blur-md">
      <div className="space-y-3">
        <Label className="text-clay-text">Ordenar por</Label>
        <RadioGroup
          value={criterion}
          onValueChange={(value) => onCriterionChange(value as OrderCriterion)}
          className="gap-2"
        >
          {CRITERIA.map((item) => (
            <label
              key={item.value}
              htmlFor={`criterion-${item.value}`}
              className={`flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 transition-colors ${criterion === item.value ? "bg-clay-surface shadow-clay-input" : "hover:bg-clay-surface/50"}`}
            >
              <RadioGroupItem
                value={item.value}
                id={`criterion-${item.value}`}
                className="border-clay-border text-clay-primary"
              />
              <span className="text-clay-text">{item.label}</span>
            </label>
          ))}
        </RadioGroup>
      </div>

      <div className="space-y-3">
        <Label htmlFor="turno-select" className="text-clay-text">
          Turno
        </Label>
        <Select
          value={turno}
          onValueChange={(value) => onTurnoChange(value as TurnoFilter)}
        >
          <SelectTrigger
            id="turno-select"
            className="rounded-2xl border-0 bg-[#f4f1fa] shadow-clay-input focus:ring-2 focus:ring-clay-primary focus:ring-offset-2"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="rounded-clay border-0 bg-white/95 shadow-clay-lg backdrop-blur-md">
            <SelectItem value="matutino">Matutino</SelectItem>
            <SelectItem value="vespertino">Vespertino</SelectItem>
            <SelectItem value="mixto">Mixto</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-clay-text">Rango horario</Label>
          <span className="text-sm font-mono text-clay-text-secondary">
            {formatHour(timeRange[0])} - {formatHour(timeRange[1])}
          </span>
        </div>
        <Slider
          value={timeRange}
          min={360}
          max={1320}
          step={30}
          onValueChange={(value) => onTimeRangeChange(value as [number, number])}
          className="py-2"
        />
      </div>

      <div className="space-y-3">
        <Label className="text-clay-text">Excluir Profesores</Label>
        <MultiSelect 
          options={availableProfessors} 
          selected={excludeProfessors} 
          onChange={(val) => onExcludeProfessorsChange?.(val)} 
          placeholder="Seleccionar profesores" 
        />
      </div>

      <div className="space-y-3">
        <Label htmlFor="max-results-select" className="text-clay-text">
          Máximo de resultados
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
                {option} opciones
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
