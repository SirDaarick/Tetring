/** Selector de materias con checkbox para el generador.
 *
 * Incluye opción "seleccionar todas" con estado tri-state.
 */
import type { ReactElement } from "react";

import { Checkbox } from "@/components/ui/checkbox";

export interface SubjectOption {
  clave: string;
  nombre: string;
  creditos: number;
}

interface SubjectSelectorProps {
  subjects: SubjectOption[];
  selected: string[];
  onSelectionChange: (selected: string[]) => void;
}

export function SubjectSelector({
  subjects,
  selected,
  onSelectionChange,
}: SubjectSelectorProps): ReactElement {
  const allSelected = subjects.length > 0 && selected.length === subjects.length;

  function toggleAll(): void {
    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(subjects.map((subject) => subject.clave));
    }
  }

  function toggleSubject(clave: string): void {
    const next = selected.includes(clave)
      ? selected.filter((item) => item !== clave)
      : [...selected, clave];
    onSelectionChange(next);
  }

  return (
    <div className="space-y-3 rounded-clay border-0 bg-white/70 p-4 shadow-clay backdrop-blur-md">
      <label
        htmlFor="subject-all"
        className="flex cursor-pointer items-center gap-3 rounded-xl p-2 transition-colors hover:bg-clay-surface/50"
      >
        <Checkbox
          id="subject-all"
          checked={allSelected}
          onCheckedChange={toggleAll}
          className="rounded-md border-clay-border data-[state=checked]:border-clay-primary data-[state=checked]:bg-clay-primary"
        />
        <span className="font-medium text-clay-text">Seleccionar todas</span>
      </label>

      <div className="space-y-1">
        {subjects.map((subject) => (
          <label
            key={subject.clave}
            htmlFor={`subject-${subject.clave}`}
            className="flex cursor-pointer items-center gap-3 rounded-xl p-2 transition-colors hover:bg-clay-surface/50"
          >
            <Checkbox
              id={`subject-${subject.clave}`}
              checked={selected.includes(subject.clave)}
              onCheckedChange={() => toggleSubject(subject.clave)}
              className="rounded-md border-clay-border data-[state=checked]:border-clay-primary data-[state=checked]:bg-clay-primary"
            />
            <span className="flex-1 text-clay-text">{subject.nombre}</span>
            <span className="text-xs text-clay-text-secondary">
              {subject.creditos} créd
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}
