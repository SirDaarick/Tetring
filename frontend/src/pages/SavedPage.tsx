/** Página de horarios guardados.
 *
 * Muestra los horarios favoritos del usuario en formato de tabla vertical.
 */
import type { ReactElement } from "react";

import { AppShell } from "@/components/layout/AppShell";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Star, Trash2, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, type SavedScheduleResponse } from "@/lib/api";
import { toast } from "sonner";

function SavedPage(): ReactElement {
  const queryClient = useQueryClient();

  const { data: schedules, isLoading } = useQuery({
    queryKey: ["schedules", "saved"],
    queryFn: () => api.get<SavedScheduleResponse[]>("/schedules/saved").then(res => res.data)
  });

  const toggleFavorite = useMutation({
    mutationFn: (id: string) => api.put(`/schedules/saved/${id}/favorite`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["schedules", "saved"] }),
    onError: () => toast.error("Error al actualizar el estado de favorito")
  });

  const deleteSchedule = useMutation({
    mutationFn: (id: string) => api.delete(`/schedules/saved/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules", "saved"] });
      toast.success("Horario eliminado");
    },
    onError: () => toast.error("Error al eliminar el horario")
  });

  return (
    <AppShell>
      <div className="flex flex-col gap-1 mb-6">
        <h1 className="text-2xl font-bold text-clay-text flex items-center gap-2">
          <Calendar className="h-7 w-7 text-clay-primary" />
          Mis Horarios Guardados
        </h1>
        <p className="text-sm text-clay-text-secondary">
          Consulta y gestiona las combinaciones que has seleccionado para tu semestre.
        </p>
      </div>

      {isLoading ? (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-clay-lg border-0 bg-white/70 p-8 shadow-clay backdrop-blur-md text-center">
          <p className="text-clay-text-secondary">Cargando horarios...</p>
        </div>
      ) : schedules && schedules.length > 0 ? (
        <div className="space-y-8">
          {schedules.map((schedule, idx) => (
            <div
              key={schedule.id}
              className="rounded-clay-2xl bg-white/70 p-6 shadow-clay backdrop-blur-md border border-clay-border/10 transition-all duration-300 hover:shadow-clay-lg"
            >
              {/* Encabezado del Horario */}
              <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-3 border-b border-clay-border/10">
                <div className="flex items-center gap-3">
                  <span className="flex items-center justify-center h-8 w-8 rounded-xl bg-clay-primary/10 text-clay-primary text-sm font-bold">
                    {idx + 1}
                  </span>
                  <h2 className="text-lg font-bold text-clay-text">
                    {schedule.name}
                  </h2>
                  <button
                    onClick={() => toggleFavorite.mutate(schedule.id)}
                    className="p-1 rounded-lg hover:bg-clay-surface transition-colors"
                    title="Marcar como favorito"
                  >
                    <Star
                      className={`h-5 w-5 ${
                        schedule.is_favorite
                          ? "fill-amber-400 text-amber-400"
                          : "text-clay-text-secondary/40 hover:text-amber-400"
                      }`}
                    />
                  </button>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteSchedule.mutate(schedule.id)}
                  className="gap-1.5 rounded-clay border-clay-border bg-white/70 px-3 py-2 text-xs text-clay-error shadow-clay transition-all hover:bg-red-50 hover:shadow-clay-lg active:scale-[0.95]"
                >
                  <Trash2 className="h-4 w-4" />
                  Eliminar Horario
                </Button>
              </div>

              {/* Tabla de Materias */}
              <div className="overflow-x-auto rounded-clay-lg border border-clay-border/30 bg-white/40 shadow-clay-pressed p-1">
                <table className="w-full border-collapse text-left text-sm text-clay-text">
                  <thead>
                    <tr className="border-b border-clay-border/20 text-xs font-bold uppercase tracking-wider text-clay-text-secondary/80 bg-clay-surface/20">
                      <th className="p-3">Clave</th>
                      <th className="p-3">Materia</th>
                      <th className="p-3">Grupo</th>
                      <th className="p-3">Profesor</th>
                      <th className="p-3">Horario</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-clay-border/10">
                    {schedule.groups.map((group) => {
                      const days = [];
                      if (group.lunes) days.push(`Lun: ${group.lunes}`);
                      if (group.martes) days.push(`Mar: ${group.martes}`);
                      if (group.miercoles) days.push(`Mié: ${group.miercoles}`);
                      if (group.jueves) days.push(`Jue: ${group.jueves}`);
                      if (group.viernes) days.push(`Vie: ${group.viernes}`);
                      const scheduleStr = days.join(" | ") || "Sin horario";

                      return (
                        <tr key={group.clave} className="hover:bg-clay-surface/30 transition-colors">
                          <td className="p-3 font-mono text-xs text-clay-text-secondary">
                            {group.clave}
                          </td>
                          <td className="p-3 font-bold text-clay-text">
                            {group.asignatura}
                          </td>
                          <td className="p-3">
                            <span className="inline-block text-[10px] px-2 py-0.5 font-bold uppercase rounded-md bg-clay-primary-soft/10 text-clay-primary border border-clay-primary-soft/20">
                              {group.grupo}
                            </span>
                          </td>
                          <td className="p-3 text-clay-text-secondary">
                            {group.profesor}
                          </td>
                          <td className="p-3 font-mono text-xs text-clay-primary">
                            {scheduleStr}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-clay-lg border-0 bg-white/70 p-8 shadow-clay backdrop-blur-md text-center">
          <p className="mb-2 text-lg font-semibold text-clay-text">
            Aún no has guardado ningún horario
          </p>
          <p className="text-clay-text-secondary">
            Genera combinaciones sin choques y guarda tus favoritos.
          </p>
        </div>
      )}
    </AppShell>
  );
}

export default SavedPage;
