/** Página del generador de horarios.
 *
 * Panel de filtros a la izquierda y resultados a la derecha. Permite
 * seleccionar materias, ajustar criterios y guardar combinaciones favoritas.
 */
import type { ReactElement } from "react";
import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Puzzle, Calendar, Sparkles, Loader2 } from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Accordion } from "@/components/ui/accordion";
import { SubjectSelector } from "@/components/scheduler/SubjectSelector";
import { GroupOfferDialog } from "@/components/scheduler/GroupOfferDialog";
import {
  FilterPanel,
  type OrderCriterion,
  type TurnoFilter,
  type MaxResults,
} from "@/components/scheduler/FilterPanel";
import {
  ScheduleCard,
  type ScheduleResult,
} from "@/components/scheduler/ScheduleCard";
import { SaveScheduleDialog } from "@/components/scheduler/SaveScheduleDialog";
import {
  api,
  extractErrorMessage,
  type PendingSubjectResponse,
  type GenerateScheduleRequest,
  type SaveScheduleRequest,
  type SavedScheduleResponse,
} from "@/lib/api";

function ResultsSkeleton(): ReactElement {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, index) => (
        <div
          key={index}
          className="h-48 rounded-clay-lg border-0 bg-white/70 shadow-clay backdrop-blur-md"
        />
      ))}
    </div>
  );
}

function EmptyResults({ onAdjust }: { onAdjust: () => void }): ReactElement {
  return (
    <div className="flex flex-col items-center justify-center rounded-clay-xl border-0 bg-white/70 p-10 text-center shadow-clay backdrop-blur-md">
      <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-clay-surface text-clay-primary shadow-clay">
        <Puzzle className="h-10 w-10" />
      </div>
      <h3 className="mb-2 text-lg font-semibold text-clay-text">
        No hay combinaciones sin choques
      </h3>
      <p className="mb-6 max-w-sm text-clay-text-secondary">
        Intenta ajustar los filtros, ampliar el rango horario o seleccionar más
        materias.
      </p>
      <button
        type="button"
        onClick={onAdjust}
        className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary px-6 py-3 font-semibold text-white shadow-clay transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
      >
        Ajustar filtros
      </button>
    </div>
  );
}

export default function SchedulerPage(): ReactElement {
  const location = useLocation();
  const queryClient = useQueryClient();

  const initialSelected = useMemo(() => {
    const state = location.state as { selectedSubjects?: string[] } | null;
    return state?.selectedSubjects ?? [];
  }, [location.state]);

  const [selectedSubjects, setSelectedSubjects] = useState<string[]>(
    () => initialSelected
  );
  const [criterion, setCriterion] = useState<OrderCriterion>(() => "compact");
  const [turno, setTurno] = useState<TurnoFilter>(() => "mixto");
  const [timeRange, setTimeRange] = useState<[number, number]>(() => [420, 1320]);
  const [maxResults, setMaxResults] = useState<MaxResults>(() => 50);
  const [results, setResults] = useState<ScheduleResult[]>(() => []);
  const [openCards, setOpenCards] = useState<string[]>(() => []);
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(() => new Set());
  const [saveSchedule, setSaveSchedule] = useState<ScheduleResult | null>(null);
  const [saveDialogOpen, setSaveDialogOpen] = useState(() => false);
  const [offerDialogOpen, setOfferDialogOpen] = useState(() => false);
  const [pinnedGroups, setPinnedGroups] = useState<Record<string, string>>({});

  const handleTogglePin = (clave: string, grupo: string) => {
    setPinnedGroups((prev) => {
      const next = { ...prev };
      if (next[clave] === grupo) {
        delete next[clave];
      } else {
        next[clave] = grupo;
      }
      return next;
    });
  };

  const { data: pending, isLoading: pendingLoading } = useQuery<
    PendingSubjectResponse[]
  >({
    queryKey: ["dashboard", "pending"],
    queryFn: () =>
      api.get<PendingSubjectResponse[]>("/dashboard/pending").then((res) => res.data),
  });

  const subjectOptions = useMemo(
    () =>
      (pending ?? []).map((subject) => ({
        clave: subject.clave,
        nombre: subject.nombre,
        creditos: subject.creditos,
        semestre: subject.semestre,
        tipo: subject.tipo,
      })),
    [pending]
  );

  const generateMutation = useMutation<
    ScheduleResult[],
    unknown,
    GenerateScheduleRequest
  >({
    mutationKey: ["schedules", "generate"],
    mutationFn: (payload) =>
      api
        .post<{ total_generated: number; results: any[] }>("/schedules/generate", payload)
        .then((res) =>
          res.data.results.map((item) => ({
            id: String(item.index),
            rank: item.index + 1,
            label: `Horario Combinado #${item.index + 1}`,
            freeHours: item.scores.compactness ?? 0,
            groups: item.groups.map((g: any) => {
              const days = [];
              if (g.lunes) days.push(`Lun ${g.lunes}`);
              if (g.martes) days.push(`Mar ${g.martes}`);
              if (g.miercoles) days.push(`Mie ${g.miercoles}`);
              if (g.jueves) days.push(`Jue ${g.jueves}`);
              if (g.viernes) days.push(`Vie ${g.viernes}`);
              return {
                ...g,
                lunes: g.lunes,
                martes: g.martes,
                miercoles: g.miercoles,
                jueves: g.jueves,
                viernes: g.viernes,
                horario: days.join(" | ") || "Sin horario",
                cupo: 40,
                disponibles: 40,
              };
            }),
          }))
        ),
    onSuccess: (data) => {
      setResults(data);
      setOpenCards(data.length > 0 ? [data[0].id] : []);
      toast.success(`${data.length} combinaciones encontradas`);
    },
    onError: (err) => {
      toast.error(`Error al generar: ${extractErrorMessage(err)}`);
    },
  });

  const saveMutation = useMutation<SavedScheduleResponse, unknown, SaveScheduleRequest>({
    mutationKey: ["schedules", "save"],
    mutationFn: (payload) =>
      api.post<SavedScheduleResponse>("/schedules/save", payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules", "saved"] });
      toast.success("Horario guardado");
      setSaveDialogOpen(false);
      setSaveSchedule(null);
    },
    onError: (err) => {
      toast.error(`No se pudo guardar: ${extractErrorMessage(err)}`);
    },
  });

  useEffect(() => {
    if (initialSelected.length > 0) {
      setSelectedSubjects(initialSelected);
    }
  }, [initialSelected]);

  function handleGenerate(): void {
    if (selectedSubjects.length === 0) {
      return;
    }

    generateMutation.mutate({
      subject_claves: selectedSubjects,
      turno: turno === "mixto" ? undefined : turno,
      scoring: [criterion],
      pinned_groups: pinnedGroups,
      filters: {
        start_min: timeRange[0],
        start_max: timeRange[1],
      },
      max_results: maxResults,
    });
  }

  function toggleFavorite(id: string): void {
    setFavoriteIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function handleSave(schedule: ScheduleResult): void {
    setSaveSchedule(schedule);
    setSaveDialogOpen(true);
  }

  function handleSaveConfirm(name: string): void {
    if (!saveSchedule) {
      return;
    }
    saveMutation.mutate({
      name,
      groups: saveSchedule.groups,
    });
  }

  function scrollToFilters(): void {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-clay-text">
            Generador de Horarios
          </h1>
          <p className="text-clay-text-secondary text-sm">
            Crea combinaciones de horarios y consulta la oferta del SAES.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={() => setOfferDialogOpen(true)}
          className="gap-2 rounded-2xl border-clay-border/50 bg-white/70 shadow-clay hover:bg-clay-surface active:scale-[0.95]"
        >
          <Calendar className="h-4 w-4 text-clay-primary" />
          Ver oferta de grupos
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[25%_75%]">
        <div className="space-y-6 lg:sticky lg:top-6 lg:self-start">
          <Button
            type="button"
            onClick={handleGenerate}
            disabled={selectedSubjects.length === 0 || generateMutation.isPending}
            className="w-full gap-2 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary text-white shadow-clay py-4 text-base font-bold hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.95] transition-all duration-300 disabled:opacity-60"
          >
            {generateMutation.isPending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="h-5 w-5" />
            )}
            {generateMutation.isPending ? "Generando..." : "Generar Horarios"}
          </Button>

          <SubjectSelector
            subjects={subjectOptions}
            selected={selectedSubjects}
            onSelectionChange={setSelectedSubjects}
            isLoading={pendingLoading}
            pinnedGroups={pinnedGroups}
          />
          <FilterPanel
            criterion={criterion}
            onCriterionChange={setCriterion}
            turno={turno}
            onTurnoChange={setTurno}
            timeRange={timeRange}
            onTimeRangeChange={setTimeRange}
            maxResults={maxResults}
            onMaxResultsChange={setMaxResults}
          />
        </div>

        <div className="min-h-[400px] min-w-0">
          {generateMutation.isPending ? (
            <ResultsSkeleton />
          ) : results.length === 0 ? (
            <div className="flex min-h-[400px] items-center justify-center rounded-clay-lg border-0 bg-white/70 p-8 shadow-clay backdrop-blur-md">
              <p className="text-center text-clay-text-secondary">
                Selecciona materias y presiona Generar para ver resultados.
              </p>
            </div>
          ) : (
            <Accordion
              value={openCards}
              onValueChange={(value) => setOpenCards(value)}
              className="space-y-4"
            >
              {results.map((schedule) => (
                <ScheduleCard
                  key={schedule.id}
                  schedule={schedule}
                  isFavorite={favoriteIds.has(schedule.id)}
                  onToggleFavorite={() => toggleFavorite(schedule.id)}
                  onSave={() => handleSave(schedule)}
                />
              ))}
            </Accordion>
          )}

          {results.length === 0 && generateMutation.isIdle ? null : null}

          {!generateMutation.isPending &&
          generateMutation.isSuccess &&
          results.length === 0 ? (
            <div className="mt-4">
              <EmptyResults onAdjust={scrollToFilters} />
            </div>
          ) : null}
        </div>
      </div>

      <SaveScheduleDialog
        open={saveDialogOpen}
        onOpenChange={setSaveDialogOpen}
        schedule={saveSchedule}
        onSave={handleSaveConfirm}
        isSaving={saveMutation.isPending}
      />

      <GroupOfferDialog
        open={offerDialogOpen}
        onOpenChange={setOfferDialogOpen}
        pinnedGroups={pinnedGroups}
        onTogglePin={handleTogglePin}
      />
    </AppShell>
  );
}
