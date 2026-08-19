/** Diálogo para guardar un horario generado con nombre personalizado.
 *
 * Recibe el horario a guardar y el callback para persistirlo.
 */
import type { ReactElement } from "react";
import { useEffect, useState } from "react";

import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ScheduleResult } from "@/components/scheduler/ScheduleCard";

interface SaveScheduleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  schedule: ScheduleResult | null;
  onSave: (name: string) => void;
  isSaving?: boolean;
}

export function SaveScheduleDialog({
  open,
  onOpenChange,
  schedule,
  onSave,
  isSaving,
}: SaveScheduleDialogProps): ReactElement {
  const [name, setName] = useState(() => "");

  useEffect(() => {
    setName(schedule?.label ?? "");
  }, [schedule]);

  function handleSave(): void {
    const trimmed = name.trim();
    if (!trimmed || isSaving) {
      return;
    }
    onSave(trimmed);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-clay-xl border-0 bg-white/90 p-6 shadow-clay-lg backdrop-blur-md sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-clay-text">Guardar horario</DialogTitle>
          <DialogDescription className="text-clay-text-secondary">
            Asigna un nombre para identificar este horario en tu lista de
            guardados.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <Label htmlFor="schedule-name" className="text-clay-text">
            Nombre del horario
          </Label>
          <Input
            id="schedule-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ej. Horario ideal"
            disabled={isSaving}
            className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleSave();
              }
            }}
          />
        </div>

        <DialogFooter className="flex-col-reverse gap-2 sm:flex-row">
          <DialogClose
            render={
              <Button
                type="button"
                variant="outline"
                disabled={isSaving}
                className="rounded-2xl border-clay-border bg-white/70 px-5 py-5 text-clay-text shadow-clay transition-all hover:-translate-y-0.5 hover:bg-white hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              >
                Cancelar
              </Button>
            }
          />
          <Button
            type="button"
            onClick={handleSave}
            disabled={!name.trim() || isSaving}
            className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary px-5 py-5 font-semibold text-white shadow-clay transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Guardando...
              </>
            ) : (
              "Guardar"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
