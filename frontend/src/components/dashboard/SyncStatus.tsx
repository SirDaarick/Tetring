/** Indicador de estado de sincronización del SAES.
 *
 * Muestra la última sincronización y un botón para refrescar los datos.
 */
import type { ReactElement } from "react";

import { Loader2, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface SyncStatusProps {
  lastSyncAt?: string | null;
  isLoading?: boolean;
  onSync: () => void;
}

function formatTimeAgo(dateString?: string | null): string {
  if (!dateString) {
    return "Sin sincronizar";
  }

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMin < 1) {
    return "Sincronizado hace un momento";
  }
  if (diffMin < 60) {
    return `Sincronizado hace ${diffMin} min`;
  }
  if (diffHours < 24) {
    return `Sincronizado hace ${diffHours} h`;
  }
  if (diffDays === 1) {
    return "Sincronizado ayer";
  }
  return `Sincronizado hace ${diffDays} días`;
}

export function SyncStatus({
  lastSyncAt,
  isLoading,
  onSync,
}: SyncStatusProps): ReactElement {
  const hasSync = Boolean(lastSyncAt);
  const label = formatTimeAgo(lastSyncAt);

  return (
    <div className="flex flex-wrap items-center gap-3">
      <Badge
        variant="outline"
        className={`rounded-full border-0 px-3 py-1 text-xs font-medium shadow-clay-input ${
          hasSync
            ? "bg-emerald-500/10 text-emerald-700"
            : "bg-amber-500/10 text-amber-700"
        }`}
      >
        <span
          className={`mr-1.5 inline-block h-2 w-2 rounded-full ${
            hasSync ? "bg-emerald-500" : "bg-amber-500"
          }`}
        />
        {label}
      </Badge>

      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={isLoading}
        onClick={onSync}
        className="gap-2 rounded-clay border-clay-border bg-white/70 px-4 py-2 text-sm font-medium text-clay-text shadow-clay transition-all hover:-translate-y-0.5 hover:bg-white hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <RefreshCw className="h-4 w-4" />
        )}
        {isLoading ? "Sincronizando..." : "Sincronizar ahora"}
      </Button>
    </div>
  );
}
