/** Punto de entrada de la aplicación React.
 *
 * Monta el árbol de componentes en el elemento #root.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import { App } from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
