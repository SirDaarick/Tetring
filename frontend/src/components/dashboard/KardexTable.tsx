/** Tabla de historial académico (kárdex).
 *
 * Muestra clave, asignatura, calificación y periodo.
 */
import type { ReactElement } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export interface KardexEntry {
  clave: string;
  asignatura: string;
  calificacion: number;
  periodo: string;
}

interface KardexTableProps {
  entries: KardexEntry[];
}

export function KardexTable({ entries }: KardexTableProps): ReactElement {
  return (
    <div className="overflow-hidden rounded-clay-lg bg-white/70 shadow-clay backdrop-blur-md">
      <Table>
        <TableHeader>
          <TableRow className="border-clay-border hover:bg-transparent">
            <TableHead className="text-clay-text">Clave</TableHead>
            <TableHead className="text-clay-text">Asignatura</TableHead>
            <TableHead className="text-clay-text">Calif</TableHead>
            <TableHead className="text-clay-text">Per</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={4}
                className="py-8 text-center text-clay-text-secondary"
              >
                Sin datos sincronizados
              </TableCell>
            </TableRow>
          ) : (
            entries.map((entry) => (
              <TableRow
                key={entry.clave + entry.periodo}
                className="border-clay-border transition-colors hover:bg-clay-surface/50"
              >
                <TableCell className="font-mono text-sm text-clay-text">
                  {entry.clave}
                </TableCell>
                <TableCell className="text-clay-text">
                  {entry.asignatura}
                </TableCell>
                <TableCell className="font-mono text-clay-text">
                  {entry.calificacion}
                </TableCell>
                <TableCell className="font-mono text-sm text-clay-text-secondary">
                  {entry.periodo}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
