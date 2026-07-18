/** Página principal del dashboard.
 *
 * Muestra métricas, kárdex y materias pendientes.
 */
import type { ReactElement } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { KardexTable } from "@/components/dashboard/KardexTable";
import { PendingAccordion } from "@/components/dashboard/PendingAccordion";

export function DashboardPage(): ReactElement {
  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold text-clay-text">Dashboard</h1>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard value="--" label="Cursadas" />
        <MetricCard value="--" label="Promedio" />
        <MetricCard value="--" label="Pendientes" />
      </div>

      <section className="mb-8">
        <h2 className="mb-4 text-lg font-semibold text-clay-text">
          Historial Académico (Kárdex)
        </h2>
        <KardexTable entries={[]} />
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-clay-text">
          Materias Pendientes
        </h2>
        <PendingAccordion subjects={[]} selected={[]} onSelectionChange={() => {}} />
      </section>
    </AppShell>
  );
}
