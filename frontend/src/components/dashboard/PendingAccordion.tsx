/** Acordeón de materias pendientes por semestre.
 *
 * Permite seleccionar materias para enviar al generador.
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

export interface PendingSubject {
  clave: string;
  nombre: string;
  creditos: number;
  semestre: number;
}

interface PendingAccordionProps {
  subjects: PendingSubject[];
  selected: string[];
  onSelectionChange: (selected: string[]) => void;
}

export function PendingAccordion({
  subjects,
  selected,
  onSelectionChange,
}: PendingAccordionProps): ReactElement {
  const [openSemester, setOpenSemester] = useState<string>("");

  const bySemester = useMemo(() => {
    const groups = new Map<number, PendingSubject[]>();
    for (const subject of subjects) {
      const list = groups.get(subject.semestre) ?? [];
      list.push(subject);
      groups.set(subject.semestre, list);
    }
    return Array.from(groups.entries()).sort(([a], [b]) => a - b);
  }, [subjects]);

  function toggleSubject(clave: string): void {
    const next = selected.includes(clave)
      ? selected.filter((item) => item !== clave)
      : [...selected, clave];
    onSelectionChange(next);
  }

  return (
    <Accordion
      value={openSemester ? [openSemester] : []}
      onValueChange={(value) => setOpenSemester(value[0] ?? "")}
      className="space-y-3"
    >
      {bySemester.map(([semestre, list]) => (
        <AccordionItem
          key={semestre}
          value={String(semestre)}
          className="overflow-hidden rounded-clay border-0 bg-white/70 shadow-clay backdrop-blur-md"
        >
          <AccordionTrigger className="px-5 py-4 text-left text-clay-text hover:no-underline">
            Semestre {semestre}
          </AccordionTrigger>
          <AccordionContent className="px-5 pb-4">
            <div className="space-y-3">
              {list.map((subject) => (
                <label
                  key={subject.clave}
                  htmlFor={`pending-${subject.clave}`}
                  className="flex cursor-pointer items-center gap-3 rounded-xl p-2 transition-colors hover:bg-clay-surface/50"
                >
                  <Checkbox
                    id={`pending-${subject.clave}`}
                    checked={selected.includes(subject.clave)}
                    onCheckedChange={() => toggleSubject(subject.clave)}
                    className="rounded-md border-clay-border data-[state=checked]:border-clay-primary data-[state=checked]:bg-clay-primary"
                  />
                  <span className="flex-1 text-clay-text">{subject.nombre}</span>
                  <span className="text-sm text-clay-text-secondary">
                    {subject.creditos} créd
                  </span>
                </label>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
