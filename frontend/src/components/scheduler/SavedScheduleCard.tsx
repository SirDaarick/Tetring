/** Card compacto para un horario guardado.
 *
 * Muestra nombre, fecha, indicador de favorito y vista previa de materias.
 * Incluye acciones de ver, favorito y eliminar.
 */
import type { ReactElement } from "react";
import { memo } from "react";

import { Star, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { SavedScheduleResponse } from "@/lib/api";

interface SavedScheduleCardProps {
  schedule: SavedScheduleResponse;
  onToggleFavorite: () => void;
  onDelete: () => void;
  onView: () => void;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMin < 1) {
    return "Hace un momento";
  }
  if (diffMin < 60) {
    return `Hace ${diffMin} min`;
  }
  if (diffHours < 24) {
    return `Hace ${diffHours} h`;
  }
  if (diffDays === 1) {
    return "Ayer";
  }
  return `Hace ${diffDays} días`;
}

export const SavedScheduleCard = memo(function SavedScheduleCard({
  schedule,
  onToggleFavorite,
  onDelete,
}: Omit<SavedScheduleCardProps, "onView">): ReactElement {
  return (
    <Card className="rounded-clay-2xl border-0 bg-white/70 p-0 shadow-clay backdrop-blur-md transition-all duration-300 hover:shadow-clay-lg flex flex-col h-full">
      <CardHeader className="px-5 pt-5 pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <CardTitle className="truncate text-base font-bold text-clay-text">
                {schedule.name}
              </CardTitle>
              {schedule.is_favorite ? (
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              ) : null}
            </div>
            <CardDescription className="mt-1 text-xs text-clay-text-secondary">
              {formatTimeAgo(schedule.created_at)} · {schedule.groups.length}{" "}
              {schedule.groups.length === 1 ? "materia" : "materias"}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="px-5 py-2 flex-1 space-y-3 overflow-y-auto max-h-[360px]">
        <div className="space-y-2.5">
          {schedule.groups.map((group) => {
            const days = [];
            if (group.lunes) days.push(`Lun: ${group.lunes}`);
            if (group.martes) days.push(`Mar: ${group.martes}`);
            if (group.miercoles) days.push(`Mié: ${group.miercoles}`);
            if (group.jueves) days.push(`Jue: ${group.jueves}`);
            if (group.viernes) days.push(`Vie: ${group.viernes}`);
            const scheduleStr = days.join(" | ") || "Sin horario";

            return (
              <div
                key={group.clave}
                className="p-3 rounded-2xl bg-clay-surface/50 border border-clay-border/10 shadow-clay-pressed"
              >
                <div className="flex justify-between items-start gap-2 mb-1">
                  <h4 className="font-bold text-xs text-clay-text leading-tight">
                    {group.asignatura}
                  </h4>
                  <span className="inline-block text-[9px] px-1.5 py-0.5 font-bold uppercase rounded-md bg-clay-primary-soft/10 text-clay-primary border border-clay-primary-soft/20 shrink-0">
                    {group.grupo}
                  </span>
                </div>
                <p className="text-[10px] text-clay-text-secondary">
                  Profesor: <span className="font-semibold text-clay-text">{group.profesor}</span>
                </p>
                <p className="text-[10px] text-clay-primary mt-1 font-mono flex items-center gap-1">
                  <span className="text-[11px]">🕒</span> {scheduleStr}
                </p>
              </div>
            );
          })}
        </div>
      </CardContent>

      <CardFooter className="flex justify-end gap-2 px-5 pb-5 pt-3 border-t border-clay-border/10">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onToggleFavorite}
          className="gap-1.5 rounded-clay border-clay-border bg-white/70 px-3 py-2 text-xs text-clay-text shadow-clay transition-all hover:-translate-y-0.5 hover:bg-white hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed"
        >
          <Star
            className={`h-3.5 w-3.5 ${
              schedule.is_favorite
                ? "fill-amber-400 text-amber-400"
                : "text-clay-text-secondary"
            }`}
          />
          {schedule.is_favorite ? "Favorito" : "Favorito"}
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onDelete}
          className="gap-1.5 rounded-clay border-clay-border bg-white/70 px-3 py-2 text-xs text-clay-error shadow-clay transition-all hover:-translate-y-0.5 hover:bg-red-50 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed"
        >
          <Trash2 className="h-3.5 w-3.5" />
          Eliminar
        </Button>
      </CardFooter>
    </Card>
  );
});
