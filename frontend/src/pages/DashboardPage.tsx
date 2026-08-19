/** Página principal del dashboard.
 *
 * Muestra métricas académicas, historial de kárdex y materias pendientes.
 * Integra sincronización con el SAES y navegación al generador.
 */
import type { ReactElement } from "react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  GraduationCap,
  ListTodo,
} from "lucide-react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { KardexTable, PerformanceChart } from "@/components/dashboard/KardexTable";
import { PendingAccordion } from "@/components/dashboard/PendingAccordion";
import { SyncStatus } from "@/components/dashboard/SyncStatus";
import { SaesConnectionWizard } from "@/components/saes/SaesConnectionWizard";
import {
  api,
  extractErrorMessage,
  type DashboardSummaryResponse,
  type KardexEntryResponse,
  type PendingSubjectResponse,
  type SyncResponse,
} from "@/lib/api";

function MetricCardSkeleton(): ReactElement {
  return (
    <div className="rounded-clay-lg border-0 bg-white/70 p-6 shadow-clay backdrop-blur-md">
      <Skeleton className="mb-3 h-10 w-10 rounded-xl" />
      <Skeleton className="mb-2 h-8 w-24 rounded-clay-sm" />
      <Skeleton className="h-4 w-32 rounded-clay-sm" />
    </div>
  );
}

export function DashboardPage(): ReactElement {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>(() => []);
  const [wizardOpen, setWizardOpen] = useState(false);

  const {
    data: summary,
    isLoading: summaryLoading,
    isError: summaryError,
    error: summaryErrorObj,
  } = useQuery<DashboardSummaryResponse>({
    queryKey: ["dashboard", "summary"],
    queryFn: () => api.get<DashboardSummaryResponse>("/dashboard/summary").then((res) => res.data),
  });

  const {
    data: kardex,
    isLoading: kardexLoading,
    isError: kardexError,
    error: kardexErrorObj,
  } = useQuery<KardexEntryResponse[]>({
    queryKey: ["dashboard", "kardex"],
    queryFn: () => api.get<KardexEntryResponse[]>("/dashboard/kardex").then((res) => res.data),
  });

  const {
    data: pending,
    isLoading: pendingLoading,
    isError: pendingError,
    error: pendingErrorObj,
  } = useQuery<PendingSubjectResponse[]>({
    queryKey: ["dashboard", "pending"],
    queryFn: () => api.get<PendingSubjectResponse[]>("/dashboard/pending").then((res) => res.data),
  });

  const syncMutation = useMutation<SyncResponse, unknown, void>({
    mutationKey: ["dashboard", "sync"],
    mutationFn: () => api.post<SyncResponse>("/dashboard/sync").then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Datos sincronizados correctamente");
    },
    onError: (err) => {
      toast.error(`Error al sincronizar: ${extractErrorMessage(err)}`);
    },
  });

  useEffect(() => {
    if (summaryError) {
      toast.error(`No se pudieron cargar las métricas: ${extractErrorMessage(summaryErrorObj)}`);
    }
  }, [summaryError, summaryErrorObj]);

  useEffect(() => {
    if (kardexError) {
      toast.error(`No se pudo cargar el kárdex: ${extractErrorMessage(kardexErrorObj)}`);
    }
  }, [kardexError, kardexErrorObj]);

  useEffect(() => {
    if (pendingError) {
      toast.error(`No se pudieron cargar las materias pendientes: ${extractErrorMessage(pendingErrorObj)}`);
    }
  }, [pendingError, pendingErrorObj]);

  const isSynced = Boolean(summary?.last_sync_at);

  const kardexEntries = useMemo(
    () =>
      (kardex ?? []).map((entry) => ({
        clave: entry.clave,
        asignatura: entry.asignatura,
        calificacion: entry.calificacion,
        periodo: entry.periodo,
      })),
    [kardex]
  );

  const pendingSubjects = useMemo(
    () =>
      (pending ?? []).map((subject) => ({
        clave: subject.clave,
        nombre: subject.nombre,
        creditos: subject.creditos,
        semestre: subject.semestre,
      })),
    [pending]
  );

  function handleGenerate(): void {
    navigate("/scheduler", {
      state: { selectedSubjects },
    });
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-clay-text">Dashboard</h1>
          <p className="text-clay-text-secondary">Resumen académico actual.</p>
        </div>
        <SyncStatus
          lastSyncAt={summary?.last_sync_at}
          isLoading={syncMutation.isPending || summaryLoading}
          onSync={() => syncMutation.mutate()}
        />
      </div>

      {!isSynced ? (
        <div className="flex flex-col items-center justify-center rounded-clay-xl border-0 bg-white/70 p-10 text-center shadow-clay-lg backdrop-blur-md md:p-14">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-clay-surface text-clay-primary shadow-clay">
            <CalendarDays className="h-12 w-12" />
          </div>
          <h2 className="mb-2 text-xl font-bold text-clay-text">
            Conecta tu cuenta del SAES
          </h2>
          <p className="mb-6 max-w-md text-clay-text-secondary">
            Sincroniza tus datos para ver tu progreso académico, historial de
            kárdex y materias pendientes.
          </p>
          <Button
            onClick={() => setWizardOpen(true)}
            className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary px-8 py-6 text-base font-semibold text-white shadow-clay transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
          >
            Conectar SAES
          </Button>
          <SaesConnectionWizard 
            open={wizardOpen} 
            onOpenChange={setWizardOpen} 
            onSuccess={() => {
              setWizardOpen(false);
              queryClient.invalidateQueries({ queryKey: ["dashboard"] });
              toast.success("SAES conectado correctamente");
            }} 
          />
        </div>
      ) : (
        <>
          <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {summaryLoading ? (
              <>
                <MetricCardSkeleton />
                <MetricCardSkeleton />
                <MetricCardSkeleton />
              </>
            ) : (
              <>
                <MetricCard
                  icon={BookOpen}
                  value={summary?.cursadas ?? 0}
                  label="Cursadas"
                />
                <MetricCard
                  icon={GraduationCap}
                  value={summary?.promedio ?? 0}
                  label="Promedio"
                  decimals={1}
                />
                <MetricCard
                  icon={ListTodo}
                  value={summary?.pendientes ?? 0}
                  label="Pendientes"
                  subtitle={
                    summary?.obligatorias_pendientes !== undefined && summary?.optativas_pendientes !== undefined
                      ? `${summary.obligatorias_pendientes} oblig. · ${summary.optativas_pendientes} opt.`
                      : undefined
                  }
                />
              </>
            )}
          </div>

          <section className="mb-8">
            <h2 className="mb-4 text-lg font-semibold text-clay-text">
              Historial Académico (Kárdex)
            </h2>
            {!kardexLoading && kardexEntries.length > 0 ? (
              <PerformanceChart entries={kardexEntries} />
            ) : null}
            <KardexTable entries={kardexEntries} isLoading={kardexLoading} />
          </section>

          <section>
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-clay-text">
                Materias Pendientes
              </h2>
              <Button
                onClick={handleGenerate}
                disabled={selectedSubjects.length === 0}
                className="gap-2 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-5 font-semibold text-white shadow-clay transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              >
                Generar horario con estas materias
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
            <PendingAccordion
              subjects={pendingSubjects}
              selected={selectedSubjects}
              onSelectionChange={setSelectedSubjects}
              isLoading={pendingLoading}
            />
          </section>
        </>
      )}
    </AppShell>
  );
}
