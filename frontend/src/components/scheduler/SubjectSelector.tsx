/** Selector de materias con checkbox para el generador.
 *
 * Agrupa materias pendientes por semestre en formato de acordeón vertical.
 * Distingue visualmente materias optativas y grupos obligatorios fijados.
 */
import type { ReactElement } from "react";
import { useMemo, useState } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { BookOpen } from "lucide-react";

export interface SubjectOption {
  clave: string;
  nombre: string;
  creditos: number;
  tipo?: string;
  semestre: number;
}

interface SubjectSelectorProps {
  subjects: SubjectOption[];
  selected: string[];
  onSelectionChange: (selected: string[]) => void;
  isLoading?: boolean;
  pinnedGroups?: Record<string, string>;
}

export function SubjectSelector({
  subjects,
  selected,
  onSelectionChange,
  isLoading,
  pinnedGroups = {},
}: SubjectSelectorProps): ReactElement {
  // Agrupar materias por semestre
  const groupedSubjects = useMemo(() => {
    const groups: Record<number, SubjectOption[]> = {};
    subjects.forEach((subject) => {
      const sem = subject.semestre || 0;
      if (!groups[sem]) {
        groups[sem] = [];
      }
      groups[sem].push(subject);
    });
    return groups;
  }, [subjects]);

  // Lista de semestres ordenados
  const semestres = useMemo(() => {
    return Object.keys(groupedSubjects)
      .map(Number)
      .sort((a, b) => a - b);
  }, [groupedSubjects]);

  // Estado de los items del Accordion abiertos (vacío para que comience cerrado por defecto)
  const [openSemestres, setOpenSemestres] = useState<string[]>([]);

  function toggleSubject(clave: string): void {
    const next = selected.includes(clave)
      ? selected.filter((item) => item !== clave)
      : [...selected, clave];
    onSelectionChange(next);
  }

  if (isLoading) {
    return (
      <div className="space-y-3 rounded-clay border-0 bg-white/70 p-4 shadow-clay backdrop-blur-md">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="flex items-center gap-3 animate-pulse">
            <div className="h-4 w-4 rounded bg-clay-surface" />
            <div className="h-4 flex-1 rounded bg-clay-surface" />
          </div>
        ))}
      </div>
    );
  }

  if (subjects.length === 0) {
    return (
      <div className="rounded-clay border-0 bg-white/70 p-4 text-center shadow-clay backdrop-blur-md">
        <p className="text-sm text-clay-text-secondary">
          No hay materias pendientes disponibles.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-clay-2xl border-0 bg-white/70 p-4 shadow-clay backdrop-blur-md flex flex-col gap-3">
      <div className="flex items-center justify-between border-b border-clay-border/10 pb-3">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-clay-primary" />
          <h2 className="font-bold text-clay-text text-sm uppercase tracking-wider">Materias Pendientes</h2>
        </div>
        <span className="text-xs font-mono font-bold text-clay-primary bg-clay-primary/10 px-2.5 py-0.5 rounded-full">
          {selected.length} / {subjects.length} sel
        </span>
      </div>

      <Accordion
        multiple={true}
        value={openSemestres}
        onValueChange={setOpenSemestres}
        className="space-y-2 mt-1"
      >
        {semestres.map((semestre) => {
          const list = groupedSubjects[semestre];
          const countSelectedInSemestre = list.filter((s) => selected.includes(s.clave)).length;
          const label = semestre === 0 ? "Otros periodos" : `${semestre}° Semestre`;

          return (
            <AccordionItem
              key={semestre}
              value={String(semestre)}
              className="border border-clay-border/10 rounded-xl bg-white/50 overflow-hidden shadow-clay-sm"
            >
              <AccordionTrigger className="px-3 py-2 text-left hover:no-underline hover:bg-clay-surface/30">
                <div className="flex items-center justify-between w-full pr-2">
                  <span className="font-bold text-xs text-clay-text">{label}</span>
                  <span className="text-[10px] font-mono font-bold text-clay-text-secondary bg-clay-surface/60 px-2 py-0.5 rounded-full">
                    {countSelectedInSemestre} / {list.length} sel
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-2 pb-2 pt-1 space-y-1 bg-white/20">
                {list.map((subject) => {
                  const isOptativa =
                    subject.tipo?.toLowerCase().includes("optativa") ||
                    subject.nombre.toLowerCase().includes("optativa");

                  return (
                    <label
                      key={subject.clave}
                      htmlFor={`subject-${subject.clave}`}
                      className="flex cursor-pointer items-start gap-3 rounded-lg p-2 transition-colors hover:bg-clay-surface/50"
                    >
                      <Checkbox
                        id={`subject-${subject.clave}`}
                        checked={selected.includes(subject.clave)}
                        onCheckedChange={() => toggleSubject(subject.clave)}
                        className="mt-0.5 rounded-md border-clay-border data-[state=checked]:border-clay-primary data-[state=checked]:bg-clay-primary"
                      />
                      <div className="flex-1 flex flex-col min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <span className="text-xs font-semibold text-clay-text leading-tight truncate">
                            {subject.nombre}
                          </span>
                          <span className="font-mono text-[9px] text-clay-text-secondary/70 shrink-0">
                            {subject.clave}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center justify-between gap-1 mt-1">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] text-clay-text-secondary">
                              {subject.creditos} créd.
                            </span>
                            {isOptativa && (
                              <span className="inline-flex items-center text-[9px] px-1 py-0.1 font-bold uppercase rounded-md bg-clay-primary/10 text-clay-primary border border-clay-primary-soft/10">
                                Optativa
                              </span>
                            )}
                          </div>
                          {pinnedGroups[subject.clave] && (
                            <span className="inline-flex items-center gap-1 text-[9px] px-1.5 py-0.5 font-bold uppercase rounded-md bg-amber-500/10 text-amber-600 border border-amber-500/20 shadow-clay-pressed animate-pulse shrink-0">
                              📌 {pinnedGroups[subject.clave]}
                            </span>
                          )}
                        </div>
                      </div>
                    </label>
                  );
                })}
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
    </div>
  );
}
