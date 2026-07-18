/** Página del generador de horarios.
 *
 * Panel de filtros + resultados (placeholder de wireframe).
 */
import type { ReactElement } from "react";
import { useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { SubjectSelector } from "@/components/scheduler/SubjectSelector";
import {
  FilterPanel,
  type OrderCriterion,
  type TurnoFilter,
} from "@/components/scheduler/FilterPanel";

function SchedulerPage(): ReactElement {
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
  const [criterion, setCriterion] = useState<OrderCriterion>("compact");
  const [turno, setTurno] = useState<TurnoFilter>("mixto");
  const [timeRange, setTimeRange] = useState<[number, number]>([420, 1320]);

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold text-clay-text">
        Generador de Horarios
      </h1>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[30%_1fr]">
        <div className="space-y-6">
          <SubjectSelector
            subjects={[]}
            selected={selectedSubjects}
            onSelectionChange={setSelectedSubjects}
          />
          <FilterPanel
            criterion={criterion}
            onCriterionChange={setCriterion}
            turno={turno}
            onTurnoChange={setTurno}
            timeRange={timeRange}
            onTimeRangeChange={setTimeRange}
          />
        </div>

        <div className="flex min-h-[400px] items-center justify-center rounded-clay-lg border-0 bg-white/70 p-8 shadow-clay backdrop-blur-md">
          <p className="text-center text-clay-text-secondary">
            Selecciona materias y presiona Generar para ver resultados.
          </p>
        </div>
      </div>
    </AppShell>
  );
}

export default SchedulerPage;
