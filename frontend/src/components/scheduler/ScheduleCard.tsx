/** Card de resultado de horario generado.
 *
 * Muestra el ranking, criterio y tabla de grupos seleccionados.
 */
import type { ReactElement } from "react";
import { memo } from "react";

import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { OccupancyBadge } from "@/components/scheduler/OccupancyBadge";

export interface ScheduleGroup {
  grupo: string;
  asignatura: string;
  profesor: string;
  horario: string;
  cupo: number;
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
  onToggleFavorite?: (id: string) => void;
}

export const ScheduleCard = memo(function ScheduleCard({
  schedule,
}: ScheduleCardProps): ReactElement {
  return (
    <Card className="overflow-hidden rounded-clay-lg border-0 bg-white/70 shadow-clay backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:shadow-clay-lg">
      <div className="flex items-center justify-between border-b border-clay-border px-5 py-4">
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
      </div>

      <div className="px-5 py-4">
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
                  <OccupancyBadge available={group.cupo} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
});
