import type { ReactElement } from "react";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Loader2, Calendar, Pin } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { api, type OptionItemResponse } from "@/lib/api";

interface GroupOfferDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pinnedGroups: Record<string, string>;
  onTogglePin: (clave: string, grupo: string) => void;
}

export function GroupOfferDialog({
  open,
  onOpenChange,
  pinnedGroups,
  onTogglePin,
}: GroupOfferDialogProps): ReactElement {
  const [search, setSearch] = useState("");

  const { data: groups = [], isLoading } = useQuery<OptionItemResponse[]>({
    queryKey: ["schedules", "groups"],
    queryFn: () => api.get<OptionItemResponse[]>("/schedules/groups").then((res) => res.data),
    enabled: open,
  });

  const filteredGroups = useMemo(() => {
    const q = search.toLowerCase().trim();
    if (!q) return groups;
    return groups.filter(
      (g) =>
        g.asignatura.toLowerCase().includes(q) ||
        g.profesor.toLowerCase().includes(q) ||
        g.grupo.toLowerCase().includes(q) ||
        g.clave.toLowerCase().includes(q)
    );
  }, [groups, search]);

  const renderScheduleStr = (g: OptionItemResponse): string => {
    const days = [];
    if (g.lunes) days.push(`Lun: ${g.lunes}`);
    if (g.martes) days.push(`Mar: ${g.martes}`);
    if (g.miercoles) days.push(`Mié: ${g.miercoles}`);
    if (g.jueves) days.push(`Jue: ${g.jueves}`);
    if (g.viernes) days.push(`Vie: ${g.viernes}`);
    return days.join(" | ") || "Sin horario";
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[90vw] md:max-w-5xl lg:max-w-6xl max-h-[85vh] flex flex-col p-6 rounded-clay-2xl border-0 bg-white/95 shadow-clay-lg backdrop-blur-md">
        <DialogHeader className="mb-4">
          <DialogTitle className="text-xl font-bold text-clay-text flex items-center gap-2">
            <Calendar className="h-6 w-6 text-clay-primary" />
            Oferta de Grupos y Horarios
          </DialogTitle>
          <p className="text-sm text-clay-text-secondary">
            Consulta todos los grupos ofertados en ESCOM para tus materias pendientes de este semestre.
          </p>
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-4 top-3.5 h-5 w-5 text-clay-text-secondary" />
          <input
            type="text"
            placeholder="Buscar por materia, profesor, grupo o clave..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-2xl border-0 bg-clay-surface/50 text-clay-text placeholder-clay-text-secondary/70 shadow-clay-pressed focus:outline-none focus:ring-2 focus:ring-clay-primary/50 transition-all duration-300"
          />
        </div>

        <div className="flex-1 overflow-y-auto rounded-clay-lg border border-clay-border/30 bg-white/40 shadow-clay-pressed p-1 min-h-[300px]">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-clay-text-secondary">
              <Loader2 className="h-10 w-10 animate-spin text-clay-primary" />
              <span>Consultando oferta en el SAES...</span>
            </div>
          ) : filteredGroups.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-clay-text-secondary font-medium">
              No se encontraron grupos disponibles.
            </div>
          ) : (
            <table className="w-full border-collapse text-left text-sm text-clay-text">
              <thead>
                <tr className="border-b border-clay-border/20 text-xs font-bold uppercase tracking-wider text-clay-text-secondary/80 bg-clay-surface/20">
                  <th className="p-3">Clave</th>
                  <th className="p-3">Materia</th>
                  <th className="p-3">Grupo</th>
                  <th className="p-3">Profesor</th>
                  <th className="p-3">Horario</th>
                  <th className="p-3 text-center">Obligatorio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clay-border/10">
                {filteredGroups.map((g, index) => {
                  const isPinned = pinnedGroups[g.clave] === g.grupo;
                  return (
                    <tr
                      key={`${g.clave}-${g.grupo}-${index}`}
                      className={`transition-colors ${isPinned ? "bg-clay-primary/5 hover:bg-clay-primary/10" : "hover:bg-clay-surface/30"}`}
                    >
                      <td className="p-3 font-mono font-bold text-xs text-clay-primary">
                        {g.clave}
                      </td>
                      <td className="p-3 font-semibold">{g.asignatura}</td>
                      <td className="p-3 text-center">
                        <span className="px-2.5 py-1 rounded-clay-sm bg-clay-surface text-clay-text text-xs font-bold shadow-clay">
                          {g.grupo}
                        </span>
                      </td>
                      <td className="p-3">{g.profesor}</td>
                      <td className="p-3 text-xs font-medium text-clay-text-secondary max-w-xs truncate">
                        {renderScheduleStr(g)}
                      </td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => onTogglePin(g.clave, g.grupo)}
                          className={`p-1.5 rounded-xl transition-all duration-300 ${
                            isPinned
                              ? "bg-clay-primary/20 text-clay-primary shadow-clay-pressed"
                              : "text-clay-text-secondary/40 hover:text-clay-primary hover:bg-clay-surface"
                          }`}
                          title={isPinned ? "Quitar grupo obligatorio" : "Hacer este grupo obligatorio"}
                        >
                          <Pin className={`h-4 w-4 transition-transform duration-300 ${isPinned ? "fill-clay-primary rotate-[45deg]" : ""}`} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
