# Especificación de Frontend — Tetring v2

> **Stack**: React + Vite + TypeScript + Tailwind + shadcn/ui  
> **Fase actual**: Wireframe funcional → Diseño claymorphism después  
> **Idioma**: Todo en español (México)

---

## 1. Sistema de Diseño — Claymorphism Morado

### 1.1 Paleta de colores (validada UX Pro Max)

```
┌─────────────────────────────────────────────────────────┐
│  FONDO APP            #F4F1FA  (lavanda frío — NUNCA    │
│                                blanco puro)             │
│  FONDO SECUNDARIO     #EDE4FF  (lavanda suave)          │
│  SUPERFICIE / CARDS   rgba(255,255,255,0.7) + blur     │
│                       (glass-clay híbrido)              │
│  BORDES SUAVES        #D8C9FF  (morado pastel)          │
│                                                         │
│  PRIMARIO             #7C3AED  (morado vibrante)        │
│  PRIMARIO HOVER       #6D28D9  (morado oscuro)          │
│  PRIMARIO SUAVE       #A78BFA  (morado claro)           │
│  GRADIENTE BOTÓN      #A78BFA → #7C3AED (135deg)       │
│                                                         │
│  TEXTO PRINCIPAL      #1E1B4B  (índigo oscuro) 15.2:1  │
│  TEXTO SECUNDARIO     #6B7280  (gris medio)             │
│  TEXTO TERCIARIO      #9CA3AF  (gris claro)             │
│                                                         │
│  ÉXITO                #10B981  (verde esmeralda)        │
│  ADVERTENCIA          #F59E0B  (ámbar)                  │
│  ERROR                #EF4444  (rojo)                   │
└─────────────────────────────────────────────────────────┘
```

> ⚠️ **Regla crítica UX Pro Max**: El fondo NUNCA debe ser blanco puro (`#FFFFFF`). Usar `#F4F1FA`. Las cards usan glass-clay híbrido: `rgba(255,255,255,0.7)` + `backdrop-filter: blur(12px)`.

### 1.2 Principios claymorphism (validado UX Pro Max)

| Principio | Especificación |
|-----------|---------------|
| **Bordes redondeados** | Cards: 32px, Botones: 20px, Inputs: 16px, Modales: 40px. NUNCA esquinas cuadradas. |
| **Sombras multi-capa** | Stack de 3 sombras: exterior suave + interior highlight + inset sutil. NUNCA sombra plana única. |
| **Glass-clay híbrido** | Cards con `rgba(255,255,255,0.7)` + `backdrop-filter: blur(12px)`. |
| **Fondo texturizado** | `#F4F1FA` base con gradiente radial sutil o ruido al 2-3% opacidad. |
| **Profundidad** | 3 niveles: plano (`#F4F1FA`), elevado (card glass), flotante (modal/dialog con blur más fuerte). |
| **Transiciones** | `transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1)` en elementos interactivos. |
| **Sin líneas duras** | NO usar `border: 1px solid`. Usar sombras o diferencia de bg para delimitar. |
| **Presionar = squish** | `:active { transform: scale(0.92); }` con spring `cubic-bezier(0.34, 1.56, 0.64, 1)` en 200ms. |

### 1.3 Sombras por nivel (validado UX Pro Max)

```css
/* Nivel 1 — Card glass-clay híbrida */
.card {
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  box-shadow:
    8px 8px 16px rgba(124, 58, 237, 0.08),
    -4px -4px 12px rgba(255, 255, 255, 0.9),
    inset 1px 1px 2px rgba(255, 255, 255, 0.8);
}

/* Nivel 2 — Modal / Dialog */
.modal {
  border-radius: 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  box-shadow:
    12px 12px 32px rgba(124, 58, 237, 0.15),
    -6px -6px 20px rgba(255, 255, 255, 0.95),
    inset 1px 1px 2px rgba(255, 255, 255, 0.9);
}

/* Nivel 3 — Botón presionado (squish) */
.button:active {
  transform: scale(0.92);
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow:
    inset 3px 3px 8px rgba(124, 58, 237, 0.15),
    inset -2px -2px 4px rgba(255, 255, 255, 0.7);
}

/* Input — hundido */
.input-clay {
  border-radius: 16px;
  background: #F4F1FA;
  border: none;
  box-shadow:
    inset 2px 2px 6px rgba(124, 58, 237, 0.08),
    inset -2px -2px 4px rgba(255, 255, 255, 0.8);
}

/* Botón primario — gradiente */
.btn-primary {
  border-radius: 20px;
  background: linear-gradient(135deg, #A78BFA, #7C3AED);
  color: white;
  font-weight: 600;
  box-shadow:
    4px 4px 12px rgba(124, 58, 237, 0.2),
    -2px -2px 6px rgba(255, 255, 255, 0.6);
  transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow:
    8px 8px 20px rgba(124, 58, 237, 0.3),
    -4px -4px 10px rgba(255, 255, 255, 0.7);
}
```

### 1.4 Configuración Tailwind (tailwind.config.ts)

```ts
export default {
  theme: {
    extend: {
      colors: {
        clay: {
          bg: '#f5f0ff',
          surface: '#ede4ff',
          border: '#d8c9ff',
          primary: '#7c3aed',
          'primary-hover': '#6d28d9',
          'primary-soft': '#a78bfa',
          text: '#1e1b4b',
          'text-secondary': '#6b7280',
          'text-tertiary': '#9ca3af',
        },
      },
      borderRadius: {
        clay: '16px',
        'clay-lg': '20px',
        'clay-sm': '12px',
      },
      boxShadow: {
        clay: '8px 8px 16px rgba(124, 58, 237, 0.08), -4px -4px 12px rgba(255, 255, 255, 0.9), inset 1px 1px 2px rgba(255, 255, 255, 0.8)',
        'clay-lg': '12px 12px 24px rgba(124, 58, 237, 0.12), -6px -6px 16px rgba(255, 255, 255, 0.95), inset 1px 1px 2px rgba(255, 255, 255, 0.9)',
        'clay-pressed': 'inset 3px 3px 6px rgba(124, 58, 237, 0.12), inset -2px -2px 4px rgba(255, 255, 255, 0.7)',
        'clay-input': 'inset 2px 2px 6px rgba(124, 58, 237, 0.08), inset -2px -2px 4px rgba(255, 255, 255, 0.8)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'float-in': 'floatIn 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'slide-up': 'slideUp 0.35s ease-out',
      },
      keyframes: {
        floatIn: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
};
```

### 1.5 Configuración shadcn/ui (globals.css)

```css
@layer base {
  :root {
    --background: 255 100% 97%;       /* #f5f0ff */
    --foreground: 244 47% 20%;        /* #1e1b4b */

    --card: 0 0% 100%;               /* #ffffff */
    --card-foreground: 244 47% 20%;

    --primary: 263 70% 50%;           /* #7c3aed */
    --primary-foreground: 0 0% 100%;

    --secondary: 255 92% 95%;         /* #ede4ff */
    --secondary-foreground: 244 47% 20%;

    --muted: 255 60% 93%;             /* lavanda suave */
    --muted-foreground: 215 14% 46%;

    --accent: 263 70% 50%;            /* #7c3aed */
    --accent-foreground: 0 0% 100%;

    --border: 263 50% 86%;            /* #d8c9ff */
    --input: 255 100% 97%;            /* #f5f0ff */
    --ring: 263 70% 50%;              /* #7c3aed */

    --radius: 1rem;                   /* 16px base */
  }
}
```

---

## 2. Principios UI/UX

### 2.1 Reglas de oro

| # | Regla | Por qué |
|---|-------|---------|
| 1 | **El usuario nunca debe preguntarse "¿qué hago ahora?"** | Cada pantalla tiene UNA acción principal clara. El botón primario siempre es el siguiente paso lógico. |
| 2 | **3 clics máximo para llegar a cualquier funcionalidad** | Login → Dashboard → Generar. Si algo requiere más de 3 clics, rediseñar. |
| 3 | **Feedback inmediato en TODA acción** | Spinner < 200ms, skeleton > 200ms, toast para éxito/error. NUNCA pantalla en blanco mientras carga. |
| 4 | **El vacío comunica** | Estados vacíos NO dicen "sin datos". Dicen "Empieza aquí →" con un CTA claro. |
| 5 | **Progreso visible siempre** | Stepper en wizard. Barra o contador en generación de horarios. "Paso X de Y" en flujos multi-paso. |
| 6 | **Deshacer, no confirmar** | Para acciones destructivas leves (quitar favorito), usar toast con "Deshacer" en vez de diálogo de confirmación. Para eliminar horario guardado, sí pedir confirmación. |
| 7 | **El teclado manda** | Enter envía formularios. Escape cierra modales. Tab navega entre campos. Flechas mueven sliders. |

### 2.2 Micro-interacciones

Toda interacción debe sentirse **táctil y responsiva**:

| Interacción | Efecto |
|-------------|--------|
| Hover en botón primario | Elevación suave (`translateY(-2px)` + sombra expande), 200ms ease-out |
| Click en botón | Hundimiento (`translateY(1px)` + shadow clay-pressed), 100ms |
| Hover en card | Elevación sutil (`translateY(-4px)`), sombra se expande, 300ms |
| Checkbox toggle | Escala 1 → 1.1 → 1 con bounce, 200ms |
| Aparecer elemento | `animate-float-in` (opacidad 0→1 + translateY 12→0) |
| Cambio de ruta | Fade suave entre páginas, 250ms |
| Toast | Slide-up desde abajo-derecha, 350ms |
| Dropdown / Select | Scale-in desde el trigger, 200ms |

### 2.3 Estados vacíos (Empty States)

Cada pantalla que puede estar vacía debe guiar al usuario:

| Pantalla | Estado vacío |
|----------|-------------|
| **Dashboard (sin sync)** | Ilustración de calendario vacío. Texto: "Conecta tu cuenta del SAES para ver tu progreso académico". Botón: "Sincronizar ahora" |
| **Mis horarios (vacío)** | Ilustración de reloj. Texto: "Aún no has guardado ningún horario. Genera combinaciones sin choques y guarda tus favoritos." Botón: "Ir al generador" |
| **Resultados (0 encontrados)** | Ilustración de piezas que no encajan. Texto: "No encontramos combinaciones sin empalmes con esos filtros." Sugerencia: "Intenta seleccionar más materias o ajustar el rango horario." Botón: "Ajustar filtros" |
| **Búsqueda sin resultados** | Ilustración de lupa. Texto descriptivo con sugerencias |

### 2.4 Manejo de errores

| Tipo | Presentación |
|------|-------------|
| Error de validación (422) | Mensaje inline debajo del campo, en rojo suave. El campo recibe borde rojo sutil. |
| Error de autenticación (401) | Toast: "Tu sesión expiró. Inicia sesión de nuevo." → redirige a /login después de 2s. |
| Error de conexión (0 / Network Error) | Toast persistente: "Sin conexión. Reintentando..." con spinner. Se reintenta 3 veces. |
| Error del servidor (500) | Toast: "Algo salió mal. Intenta de nuevo en un momento." |
| Error SAES (502) | Toast: "El SAES no está disponible ahora. Tus datos guardados se muestran de la última sincronización." |
| Conflicto (409) | Mensaje inline: "Esa boleta ya está vinculada a otra cuenta." |

### 2.5 Accesibilidad (a11y)

| Requisito | Implementación |
|-----------|---------------|
| Contraste mínimo 4.5:1 | `#1e1b4b` sobre `#ffffff` = 15.2:1 ✅ |
| Focus visible | Anillo morado `ring-2 ring-clay-primary ring-offset-2` en TODO elemento interactivo |
| Labels en inputs | Siempre usar `<label>` asociado con `htmlFor`. Placeholder NUNCA reemplaza label. |
| Textos alternativos | `aria-label` en iconos sin texto. `alt` en imágenes de captcha. |
| Navegación por teclado | Orden de tab lógico. Skip-to-content link. |
| Estados comunicados | Errores y éxito visibles también para lectores de pantalla (`role="alert"` en toasts) |

### 2.6 Performance percibida

| Técnica | Dónde |
|---------|-------|
| **Skeleton screens** | Dashboard, kárdex, resultados de horarios |
| **Optimistic UI** | Toggle favorito (cambia el ícono antes de que responda el server, revierte si falla) |
| **Stale-while-revalidate** | React Query con `staleTime: 30_000` para datos que no cambian seguido (kárdex, perfil) |
| **Debounce** | 300ms en inputs de búsqueda/filtro |
| **Lazy loading** | `React.lazy()` + `Suspense` para páginas que no son la inicial |

---

## 3. Flujo del usuario

```
LOGIN → ¿SAES vinculado? → NO → WIZARD DE VINCULACIÓN → SÍ → DASHBOARD
                                  (stepper 3 pasos)
```

---

## 4. Pantallas

### 4.1 Login / Register

**Dos modos en la misma pantalla** con toggle animado.

#### Layout

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│               🟦 TETRING                              │
│          Generador de Horarios IPN                    │
│                                                       │
│   ┌─────────────────────────────────────────────┐    │
│   │  [Iniciar sesión]  |  Crear cuenta           │    │ ← tabs suaves
│   │                                             │    │
│   │  Correo electrónico                         │    │
│   │  ┌─────────────────────────────────────┐    │    │
│   │  │ alumno@ipn.mx                        │    │    │ ← input clay
│   │  └─────────────────────────────────────┘    │    │
│   │                                             │    │
│   │  Contraseña                            👁️   │    │
│   │  ┌─────────────────────────────────────┐    │    │
│   │  │ ••••••••••                          │    │    │
│   │  └─────────────────────────────────────┘    │    │
│   │                                             │    │
│   │  ┌─────────────────────────────────────┐    │    │
│   │  │         Iniciar sesión              │    │    │ ← botón clay elevado
│   │  └─────────────────────────────────────┘    │    │
│   │                                             │    │
│   │  ──────── o continúa con ────────           │    │
│   │                                             │    │
│   │  ┌─────────────────────────────────────┐    │    │
│   │  │  G   Continuar con Google           │    │    │ ← botón secondary
│   │  └─────────────────────────────────────┘    │    │
│   └─────────────────────────────────────────────┘    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

**Endpoints**: `POST /api/v1/auth/login`, `POST /api/v1/auth/register`, Google OAuth redirect.

**Micro-interacciones**:
- El toggle entre Login/Register desliza un indicador suave con `transition-all duration-300`
- El botón primario se eleva en hover, se hunde en click
- El input de contraseña muestra/oculta con animación del ícono del ojo
- Error de validación: shake sutil en el campo + mensaje en rojo claro

---

### 4.2 Wizard de Vinculación SAES

Stepper horizontal con 3 pasos, cada uno animado al avanzar.

```
┌──────────────────────────────────────────────────────┐
│                                                       │
│   ●────────────────●────────────────○                 │
│   Escuela        Captcha         ¡Listo!              │
│                                                       │
│   ┌─────────────────────────────────────────────┐    │
│   │                                             │    │
│   │   ¿En qué escuela estudias?                 │    │
│   │                                             │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │ ESCOM - Escuela Superior de... ▾ │      │    │ ← select
│   │   └──────────────────────────────────┘      │    │
│   │                                             │    │
│   │   Número de boleta                          │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │ 2024000001                        │      │    │
│   │   └──────────────────────────────────┘      │    │
│   │                                             │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │         Continuar                │      │    │
│   │   └──────────────────────────────────┘      │    │
│   └─────────────────────────────────────────────┘    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

**Paso 2 — Captcha**:

```
│   ┌─────────────────────────────────────────────┐    │
│   │                                             │    │
│   │   Resuelve el captcha del SAES              │    │
│   │                                             │    │
│   │   ┌──────────────────────┐  [🔄 Recargar]  │    │
│   │   │   ██▓▒░ A3X9 ░▒▓██  │                 │    │ ← imagen captcha
│   │   └──────────────────────┘                 │    │
│   │                                             │    │
│   │   Escribe el texto                          │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │ A3X9                               │      │    │
│   │   └──────────────────────────────────┘      │    │
│   │                                             │    │
│   │   Contraseña del SAES                       │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │ ••••••••••                  👁️    │      │    │
│   │   └──────────────────────────────────┘      │    │
│   │                                             │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │         Vincular cuenta          │      │    │
│   │   └──────────────────────────────────┘      │    │
│   └─────────────────────────────────────────────┘    │
```

**Paso 3 — Confirmación**:

```
│   ┌─────────────────────────────────────────────┐    │
│   │                                             │    │
│   │               ✅                             │    │ ← animación scale-in
│   │                                             │    │
│   │        ¡Cuenta vinculada!                   │    │
│   │                                             │    │
│   │     Boleta: 2024000001                       │    │
│   │     Escuela: ESCOM                           │    │
│   │                                             │    │
│   │   ┌──────────────────────────────────┐      │    │
│   │   │       Ir al dashboard            │      │    │
│   │   └──────────────────────────────────┘      │    │
│   └─────────────────────────────────────────────┘    │
```

**Micro-interacciones**:
- Avance entre pasos: slide horizontal con fade (200ms)
- Stepper: círculo se llena con gradiente morado al completar
- Error de captcha: shake en imagen + mensaje "El texto no coincide"
- Éxito: confeti sutil o partículas (opcional, nice-to-have visual)

---

### 4.3 Dashboard

Pantalla principal. Layout: **sidebar fija izquierda + contenido scrollable**.

```
┌──────────┬──────────────────────────────────────────────┐
│          │                                               │
│ 🟦 TETRING│  📊 Dashboard                                │
│ ──────── │  ────────────────────────────────────────    │
│          │                                               │
│ 🏠 Inicio │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│          │  │   42     │  │   8.7   │  │   18     │    │
│ 🧠 Generar│  │ Cursadas │  │ Promedio│  │Pendientes│    │
│          │  └──────────┘ └──────────┘ └──────────┘    │
│ 💾 Guarda.│                                               │
│          │  📚 Historial Académico (Kárdex)              │
│ ──────── │  ┌──────────────────────────────────────┐    │
│          │  │ Clave │ Asignatura    │ Calif │ Per  │    │
│ ⚙️ Perfil │  │ B101  │ Cálculo       │ 9.5   │ 1    │    │
│          │  │ B102  │ Programación  │ 8.0   │ 1    │    │
│ 🚪 Salir  │  │ B201  │ Álgebra       │ 7.8   │ 2    │    │
│          │  └──────────────────────────────────────┘    │
│          │                                               │
│          │  📋 Materias Pendientes                        │
│          │  ┌─ Semestre 3 ─────────────────────────┐    │
│          │  │ ☑ B301 Estructuras de Datos  8 créd  │    │
│          │  │ ☐ B302 Bases de Datos       6 créd  │    │
│          │  └──────────────────────────────────────┘    │
│          │  ┌─ Semestre 4 ─────────────────────────┐    │
│          │  │ ☐ B401 Ingeniería de Software 8 créd│    │
│          │  └──────────────────────────────────────┘    │
│          │                                               │
└──────────┴──────────────────────────────────────────────┘
```

**Componentes y su comportamiento**:

| Elemento | Comportamiento |
|----------|---------------|
| **Cards de métricas** | Número grande + label debajo. Animación de conteo al cargar (0 → 42 en 1s). Sombra clay. |
| **Tabla de kárdex** | Filas con hover highlight suave. Click en fila no hace nada (solo lectura). Scroll interno si hay +10 filas. |
| **Acordeón de pendientes** | Solo UN semestre abierto a la vez. Checkbox guarda selección para el generador. Animación de altura. |
| **Botón "Sincronizar"** | Si datos desactualizados, badge sutil: "🟡 Sin sincronizar". Click → spinner → datos frescos. |
| **Sidebar** | Ítem activo con fondo `#ede4ff`. Hover: fondo `#f5f0ff`. Transición 200ms. Colapsable en mobile a íconos solos. |

**Estados**:
- **Sin sincronizar (primera vez)**: Card central grande con ilustración. "Sincroniza tus datos del SAES". Botón primario grande.
- **Sincronizando**: Las 3 cards de métricas muestran skeleton. Tabla muestra skeleton de filas.
- **Error SAES**: Toast amarillo persistente. Datos previos se siguen mostrando con badge "desactualizado".

---

### 4.4 Generador de Horarios

Layout: **panel de filtros (30% izquierda) + resultados (70% derecha)**.

```
┌──────────────┬──────────────────────────────────────────┐
│ 📋 Materias  │  🧠 Resultados                            │
│              │                                           │
│ ☑ Todas     │  ┌─ 🏅 #1 · Compacto · ★ 2.5 hrs libres─┐│
│ ☑ Cálculo   │  │ Gru │ Asignatura │ Prof │ Lun-Vie    ││
│ ☑ Prog.     │  │ 1MV1│ Cálculo    │ López│ 7-8:30     ││
│ ☐ Álgebra   │  │ 1MV2│ Programac. │ García│ 8:30-10   ││
│ ☑ Estruct.  │  │ ...                                   ││
│              │  │ 🟢🟢🟡🟢🟢  ⭐ Guardar  💾 Nombrar  ││
│ ──────────  │  └──────────────────────────────────────┘│
│ 🎯 Orden     │                                           │
│ ○ Compacto  │  ┌─ 🏅 #2 · Entrada 9am · ★ 4.0 hrs ───┐│
│ ● Tarde     │  │ [Tabla similar...]                    ││
│ ○ Libre     │  └──────────────────────────────────────┘│
│              │                                           │
│ ──────────  │  ┌─ 🏅 #3 · Libre vie · ★ 6.5 hrs ─────┐│
│ 🔍 Filtros   │  │ [Tabla similar...]                    ││
│ Turno        │  └──────────────────────────────────────┘│
│ [Matutino ▾]│                                           │
│              │                   1-20 de 156 ▸ ▸▸ ▸▸▸  │
│ Hora         │                                           │
│ [07:00─•─────────22:00]                                │
│              │                                           │
│ ┌──────────┐ │                                           │
│ │ 🚀 Generar│ │                                           │
│ └──────────┘ │                                           │
└──────────────┴──────────────────────────────────────────┘
```

**Componentes y su comportamiento**:

| Elemento | Comportamiento |
|----------|---------------|
| **Checkboxes materias** | Con badge de créditos. "Seleccionar todas" con estado tri-state (todas/ninguna/algunas). |
| **Radio criterio** | Cambio inmediato — reordena resultados ya generados si existen, sin recalcular. |
| **Slider de hora** | Rango dual. Labels muestran "07:00" y "22:00". Paso de 30 min. Snaps suaves. |
| **Botón Generar** | Ocupa todo el ancho del panel. Animación de pulso suave cuando hay checkboxes seleccionados (llama la atención). Deshabilitado y gris cuando no hay selección. |
| **Cards de resultados** | Accordion. Solo una abierta a la vez. La #1 abierta por defecto. |
| **Badges de cupo** | 🟢 disponible, 🟡 bajo, 🟠 crítico, 🔴 lleno. Tooltip con número exacto al hover. |
| **Paginación** | Mostrando "1-20 de 156". Botones de página con números, no solo "siguiente". |
| **Botón ⭐** | Optimistic: cambia a relleno inmediatamente, revierte si la API falla. |
| **Botón Guardar** | Abre un dialog pequeño: input de nombre + botón "Guardar". |

**Estados**:
- **Generando**: El botón se reemplaza por spinner + "Calculando combinaciones...". El panel de resultados muestra skeleton de 5 cards.
- **0 resultados**: Ilustración de piezas de rompecabezas. "No hay combinaciones sin choques. Intenta seleccionar menos materias o ampliar el horario."
- **Error**: Toast. Los resultados previos (si hay) no se borran.

---

### 4.5 Mis Horarios Guardados

```
┌──────────┬──────────────────────────────────────────────┐
│          │  💾 Mis Horarios Guardados                    │
│          │                                               │
│          │  ┌──────────────────────┐ ┌────────────────┐ │
│          │  │ ⭐ Horario Ideal     │ │ Opción B       │ │
│          │  │ 5 materias           │ │ 4 materias     │ │
│          │  │ Creado: hace 2 días  │ │ Creado: ayer   │ │
│          │  │ 🟢🟢🟡🟢 — 3/4 ok  │ │ 🟢🟢🟢🟢 — ok  │ │
│          │  │ ─────────────────── │ │ ───────────── │ │
│          │  │ [Ver] [🗑️]         │ │ [Ver] [🗑️]    │ │
│          │  └──────────────────────┘ └────────────────┘ │
│          │                                               │
│          │  ┌──────────────────────┐ ┌────────────────┐ │
│          │  │ Plan B              │ │ Respaldo       │ │
│          │  │ 5 materias           │ │ 5 materias     │ │
│          │  │ ...                  │ │ ...            │ │
│          │  └──────────────────────┘ └────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Endpoints**: `GET /api/v1/schedules/saved`, `PUT .../favorite`, `DELETE .../{id}`.

**Estados**:
- **Vacío**: Ilustración + CTA al generador.
- **Expandido**: Modal/dialog con tabla completa + badges de cupo actualizados.

---

### 4.6 Perfil

```
┌──────────┬──────────────────────────────────────────────┐
│          │  ⚙️ Configuración                              │
│          │                                               │
│          │  ┌──────────────────────────────────────┐    │
│          │  │  👤 Información personal              │    │
│          │  │                                      │    │
│          │  │  Correo: alumno@ipn.mx               │    │
│          │  │  Nombre: [Juan Pérez          ]      │    │
│          │  │                                      │    │
│          │  │  [Guardar cambios]                   │    │
│          │  └──────────────────────────────────────┘    │
│          │                                               │
│          │  ┌──────────────────────────────────────┐    │
│          │  │  🏫 Cuenta SAES                       │    │
│          │  │                                      │    │
│          │  │  ✅ Vinculada                         │    │
│          │  │  Boleta: 2024000001                   │    │
│          │  │  Escuela: ESCOM                       │    │
│          │  │                                      │    │
│          │  │  [Desvincular cuenta del SAES]       │    │
│          │  └──────────────────────────────────────┘    │
│          │                                               │
│          │  ┌──────────────────────────────────────┐    │
│          │  │  🚪 Sesión                            │    │
│          │  │                                      │    │
│          │  │  [Cerrar sesión]                     │    │
│          │  └──────────────────────────────────────┘    │
└──────────┴──────────────────────────────────────────────┘
```

**Micro-interacciones**:
- "Desvincular" abre dialog de confirmación: "¿Desvincular tu cuenta del SAES? Perderás el acceso al kárdex y horarios. Tus horarios guardados se conservan."

---

## 5. Navegación y Layout Global

### 5.1 Sidebar

```
┌─────────────┐
│             │
│  🟦 TETRING  │  ← Logo: "TETRING" en morado, bold
│             │
│ ─────────── │
│             │
│  🏠 Inicio   │  ← active: bg #ede4ff, text #7c3aed
│  🧠 Generar  │  ← inactive: text #6b7280
│  💾 Guardado │
│             │
│ ─────────── │
│             │
│  ⚙️ Perfil  │
│  🚪 Salir   │
│             │
└─────────────┘
```

**Comportamiento**:
- Ancho: 240px en desktop
- Colapsa a 64px (solo íconos) en pantallas <1024px
- En mobile (<768px): hamburger menu → Sheet desde la izquierda
- Ítem activo tiene un indicator sutil (barra morada de 3px a la izquierda)
- Hover: `bg-[#f5f0ff]` con `transition-colors duration-200`

### 5.2 Top bar (opcional, futuro)

Para notificaciones de cupos:

```
┌──────────────────────────────────────────────────────────┐
│  [🍔]  🟦 Tetring    🔔 3 alertas    👤 JP             │
└──────────────────────────────────────────────────────────┘
```

### 5.3 Responsive breakpoints

| Breakpoint | Layout |
|------------|--------|
| ≥1024px | Sidebar visible (240px) + contenido. Generador: filtros (30%) + resultados (70%). |
| 768-1023px | Sidebar colapsado (64px). Generador: filtros (35%) + resultados (65%). |
| <768px | Sidebar → Sheet (hamburger). Todas las pantallas single-column. Generador: filtros arriba (collapsible), resultados abajo. |

---

## 6. Estados Globales

### 6.1 Autenticación

```
┌─────────────────────────────────────────────────────┐
│  App inicia                                          │
│    │                                                 │
│    ├── ¿Hay access_token en localStorage?            │
│    │     ├── No → /login                             │
│    │     └── Sí → GET /auth/me                       │
│    │               ├── 200 → renderizar app          │
│    │               └── 401 → POST /auth/refresh      │
│    │                         ├── 200 → guardar tokens, seguir │
│    │                         └── 401 → limpiar storage, /login │
└─────────────────────────────────────────────────────┘
```

### 6.2 SAES

```
┌─────────────────────────────────────────────────────┐
│  Después de login y auth:                            │
│    │                                                 │
│    ├── GET /saes/profile                             │
│    │     ├── 200 (vinculado) → dashboard             │
│    │     └── 404 (no vinculado) → wizard vinculación  │
│    │                                                 │
│  En dashboard:                                       │
│    ├── ¿Hay datos syncados?                          │
│    │     ├── No → mostrar estado "sin sincronizar"   │
│    │     └── Sí → mostrar datos + "última sync: X"   │
│    │                                                 │
│    └── ¿Datos > 24h viejos?                          │
│          └── Badge "desactualizado" + sugerir refresh │
└─────────────────────────────────────────────────────┘
```

### 6.3 Heartbeat (ocupabilidad)

```
┌─────────────────────────────────────────────────────┐
│  Cuando el usuario está en /schedules o /saved:      │
│    │                                                 │
│    └── setInterval(30s) → POST /occupancy/heartbeat  │
│                              │                       │
│                              └── 200 → seguir         │
│                                  401 → refresh token │
│                                                   │
│    Si hay horario seleccionado:                      │
│    └── EventSource → GET /occupancy/stream/{id}      │
│          └── onmessage → actualizar badges de cupo   │
└─────────────────────────────────────────────────────┘
```

---

## 7. Componentes shadcn/ui — Lista Completa

| Componente | Dónde se usa | Personalización clay |
|-----------|-------------|---------------------|
| `Button` | TODAS partes | `rounded-xl`, sombras clay, hover elevate |
| `Input` | Login, register, captcha, búsqueda | `rounded-xl`, `shadow-clay-input`, bg lavanda |
| `Card` | Dashboard metrics, horarios guardados | `rounded-2xl`, `shadow-clay`, bg blanco |
| `Table` | Kárdex, horarios, resultados | Filas con hover suave, bordes sin líneas duras |
| `Accordion` | Materias pendientes, resultados de horarios | `rounded-xl`, transición de altura suave |
| `Checkbox` | Selección de materias | Custom: círculo morado con check blanco, bounce anim |
| `RadioGroup` | Criterios de orden | Custom: pill buttons con bg lavanda |
| `Slider` | Rango horario | Track morado suave, thumb con sombra clay |
| `Select` | Turno, escuela | `rounded-xl`, dropdown con sombra clay-lg |
| `Badge` | Estados de cupo (🟢🟡🟠🔴) | `rounded-full`, colores semáforo + variante outline |
| `Sheet` / `Sidebar` | Navegación lateral | Sidebar drawer desde izquierda en mobile |
| `Toast` (sonner) | Notificaciones de error/éxito | `rounded-xl`, slide-up, colores de la paleta |
| `Skeleton` | Estados de carga | `rounded-xl`, pulso con bg lavanda |
| `Stepper` | Wizard de vinculación | Custom: círculos conectados con línea |
| `Dialog` | Confirmación de eliminar, modal de guardar | `rounded-2xl`, `shadow-clay-lg`, overlay con blur |
| `Tooltip` | Ayuda contextual en iconos | `rounded-lg`, bg índigo oscuro, texto blanco |
| `Separator` | Divisores visuales | Línea sutil con gradiente transparente → morado → transparente |
| `Tabs` | Login/Register toggle | `rounded-xl`, pill indicator animado |
| `Avatar` | Foto de perfil (Google) | `rounded-full`, borde morado 2px |
| `Progress` | Barra de generación (opcional) | Track lavanda, fill gradiente morado |

---

## 8. Resumen de endpoints que consume el frontend

```
AUTH
  POST /api/v1/auth/register         → {email, password, full_name?}
  POST /api/v1/auth/login            → {email, password}
  POST /api/v1/auth/refresh          → {refresh_token}
  GET  /api/v1/auth/me               → UserResponse
  GET  /api/v1/auth/google/login     → redirect
  GET  /api/v1/auth/google/callback  → redirect con tokens

SAES
  GET    /api/v1/saes/schools        → [{id, name, url}]
  POST   /api/v1/saes/link/start     → {boleta, school}
  POST   /api/v1/saes/link/complete  → {password, captcha_solution}
  GET    /api/v1/saes/profile        → SaesProfileResponse
  DELETE /api/v1/saes/unlink         → 204

DASHBOARD
  GET  /api/v1/dashboard/summary     → DashboardSummaryResponse
  GET  /api/v1/dashboard/kardex      → [KardexEntryResponse]
  GET  /api/v1/dashboard/pending     → [PendingSubjectResponse]
  GET  /api/v1/dashboard/schedule    → [ScheduleEntryResponse]
  POST /api/v1/dashboard/sync        → {kardex_count, curriculum_count, schedule_count}

SCHEDULES
  POST   /api/v1/schedules/generate       → {subject_claves[], turno?, scoring[], filters}
  POST   /api/v1/schedules/save           → {name, groups[]}
  GET    /api/v1/schedules/saved          → [SavedScheduleResponse]
  PUT    /api/v1/schedules/saved/{id}/favorite → 200
  DELETE /api/v1/schedules/saved/{id}     → 204

OCCUPANCY
  POST /api/v1/occupancy/heartbeat        → {active: true}
  GET  /api/v1/occupancy/check/{id}       → OccupancyCheckResponse
  GET  /api/v1/occupancy/stream/{id}      → SSE stream
```

---

## 9. Instrucciones para el mockup

### Lo que debe comunicar el diseño

1. **Confianza**: La app se siente sólida, profesional. No es un proyecto de principiante.
2. **Calma**: Los morados y lavandas transmiten tranquilidad. Un estudiante ya está estresado — la app debe ser un respiro.
3. **Claridad**: Cada pantalla tiene UNA acción principal. El ojo sabe exactamente dónde mirar.
4. **Modernidad**: Claymorphism + animaciones suaves = se siente 2026, no 2018.

### Lo que NO debe tener

- ❌ Sombras negras/grises duras (neumorfismo oscuro)
- ❌ Bordes sólidos y rectos (estilo Bootstrap)
- ❌ Colores saturados y chillones
- ❌ Textos gigantes sin jerarquía
- ❌ Formularios interminables sin división visual
- ❌ Iconos genéricos sin personalidad

### Herramientas sugeridas para mockup

- **Figma** (gratis) — ideal para claymorphism con efectos de capa
- **Penpot** (open source) — alternativa a Figma
- **Excalidraw** — para wireframes rápidos antes del diseño

### Entregables esperados del mockup

1. **3 pantallas principales**: Login → Dashboard → Generador de Horarios
2. **Componentes clave**: Sidebar, card de métrica, tabla de kárdex, accordion de pendientes, resultado de horario con badges de cupo
3. **Flujo**: Story simple que muestre cómo se pasa de una pantalla a otra
4. **Design tokens**: confirmación visual de la paleta, sombras, tipografía

---

## 10. React Performance — Vercel Best Practices

Reglas obligatorias extraídas de la guía oficial de Vercel para React/Next.js, adaptadas a nuestro stack (React + Vite + TypeScript). Ordenadas por impacto.

### 10.1 Eliminación de Waterfalls (CRÍTICO)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`async-parallel`** | Dashboard: fetch inicial de datos | Ejecutar `getSummary()`, `getKardex()`, `getPending()` con `Promise.all()`, no secuencial. |
| **`async-suspense-boundaries`** | Todas las páginas | Cada página envuelta en `<Suspense fallback={<PageSkeleton />}>`. El skeleton DEBE tener la misma forma que el contenido para evitar CLS. |
| **`async-cheap-condition-before-await`** | Auth guard en rutas protegidas | Verificar `localStorage.getItem('token')` ANTES de llamar `GET /auth/me`. Si no hay token → redirigir inmediatamente, sin await. |

### 10.2 Bundle Size (CRÍTICO)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`bundle-dynamic-imports`** | Páginas no-iniciales | `React.lazy(() => import('./pages/GeneratorPage'))` para Generador y Perfil. Solo Dashboard carga eager. |
| **`bundle-barrel-imports`** | Todos los imports de shadcn/ui | **NO hacer** `import { Button, Input, Card } from '@/components/ui'`. Siempre importar directo: `import { Button } from '@/components/ui/button'`. |
| **`bundle-defer-third-party`** | Google Analytics, fonts | Cargar analytics DESPUÉS de hidratación: `requestIdleCallback(() => loadAnalytics())`. |
| **`bundle-preload`** | Generador de Horarios | Precargar el chunk del Generador al hacer hover en el link del sidebar: `<Link onMouseEnter={() => import('./GeneratorPage')}>`. |

### 10.3 Rendering Performance (MEDIUM)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`rendering-content-visibility`** | Kárdex (muchas filas), resultados de horarios | `content-visibility: auto` en el contenedor de la tabla. Para filas fuera de viewport. |
| **`rendering-conditional-render`** | TODOS los condicionales | **NUNCA usar `&&`**. Siempre ternario: `{isLoading ? <Spinner /> : null}`. `{count && <Badge />}` rompe si count es 0. |
| **`rendering-hoist-jsx`** | Sidebar, header, footer estáticos | Extraer JSX estático FUERA del componente: `const SIDEBAR_ITEMS = [...]` a nivel módulo, no dentro del render. |
| **`rendering-hydration-no-flicker`** | Tema dark/light, estado de auth | Usar script inline en `<head>` para leer preferencia de tema y token de localStorage ANTES del primer render. |

### 10.4 Re-render Optimization (MEDIUM)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`rerender-memo`** | Tabla de resultados en Generador | `React.memo(ScheduleResultCard)` — la tabla de horarios se re-renderiza mucho al filtrar. Memoizar cada card. |
| **`rerender-transitions`** | Slider de hora, filtro de materias | Envolver cambios de filtro con `startTransition()` para que el slider se sienta responsivo mientras los resultados se actualizan. |
| **`rerender-no-inline-components`** | TODOS los componentes | **NUNCA** definir un componente dentro de otro componente. Crea una nueva identidad en cada render, destruye el reconciliation de React. |
| **`rerender-lazy-state-init`** | Datos iniciales pesados | `useState(() => parseInitialData(props))` — función, no valor. |
| **`rerender-derived-state-no-effect`** | Cálculos derivados | `const pendingCount = useMemo(() => subjects.filter(s => !s.completed).length, [subjects])`. NUNCA `useEffect(() => setCount(...), [subjects])`. |
| **`rerender-defer-reads`** | Estado solo usado en callbacks | Si un estado solo se lee en `onClick`, no lo subscribas con `useState`. Usa `useRef`. |
| **`rerender-use-deferred-value`** | Búsqueda/filtro en kárdex | `const deferredQuery = useDeferredValue(searchQuery)` para mantener el input rápido mientras la tabla filtra. |

### 10.5 Client-Side Data Fetching (MEDIUM-HIGH)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`client-swr-dedup`** | React Query config global | Configurar `staleTime: 30_000` y `gcTime: 5 * 60_000`. Usar `queryKey` consistentes para que React Query deduplique requests automáticamente. |
| **`client-passive-event-listeners`** | Heartbeat, scroll infinito | `window.addEventListener('scroll', handler, { passive: true })`. |

### 10.6 JavaScript Performance (LOW-MEDIUM)

| Regla | Dónde aplica | Implementación |
|-------|-------------|----------------|
| **`js-set-map-lookups`** | Algoritmo de horarios (frontend) | Para verificar colisiones de slots: usar `Set.has()` → O(1), no `Array.includes()` → O(n). |
| **`js-early-exit`** | Validación de formularios | `if (!email) return setError('Email requerido')` al inicio de la función. No anidar ifs. |
| **`js-hoist-regexp`** | Validación de email, boleta | `const EMAIL_RE = /^[^\s@]+@[^\s@]+$/` a nivel módulo, NO dentro de la función de validación. |
| **`js-combine-iterations`** | Filtrado de horarios | `schedules.flatMap(s => s.groups.filter(g => g.available).map(g => ({schedule: s, group: g})))` en vez de `.filter().map()` separados. |

### 10.7 Estructura de proyecto React (convenciones)

```
frontend/src/
├── components/
│   ├── ui/              # shadcn/ui primitives (NO modificar)
│   ├── layout/           # AppShell, Sidebar, ProtectedRoute
│   ├── auth/             # LoginForm, RegisterForm, GoogleButton
│   ├── dashboard/        # KardexTable, PendingAccordion, MetricCard
│   ├── scheduler/         # SubjectSelector, FilterPanel, ScheduleCard, OccupancyBadge
│   └── professors/        # ProfessorRating (nice-to-have)
├── hooks/
│   ├── useAuth.ts         # Auth state (Zustand)
│   ├── useSaes.ts         # SAES linking flow
│   ├── useOccupancy.ts    # SSE + heartbeat
│   └── useDebounce.ts     # Debounce hook (300ms default)
├── lib/
│   ├── api.ts             # Axios instance + interceptors (401 → refresh)
│   └── query-client.ts    # React Query client config
├── pages/
│   ├── LoginPage.tsx       # lazy loaded (except Dashboard)
│   ├── DashboardPage.tsx   # eager loaded
│   ├── SchedulerPage.tsx   # lazy loaded + preload on hover
│   └── ProfilePage.tsx     # lazy loaded
├── stores/
│   └── auth-store.ts       # Zustand: user, token, login(), logout()
├── App.tsx                  # Router + QueryClientProvider + AuthProvider
└── main.tsx                 # Entry point
```

---

## 11. UX Audit — Ajustes Requeridos (UI/UX Pro Max)

Resultados de la auditoría cruzada entre el spec original, las pantallas en Stitch, y las reglas de UI/UX Pro Max. Ordenados por prioridad.

### 11.1 Críticos (afectan accesibilidad o usabilidad core)

| # | Pantalla | Regla UX violada | Corrección |
|---|----------|-----------------|------------|
| **C1** | Login, Generador | **Submit Feedback (HIGH)**: Sin indicador de carga en botones | Los botones de submit ("Ingresar", "Generar Horarios", "Vincular") DEBEN mostrar: spinner en el botón → estado de carga → éxito/error. NUNCA botón sin respuesta tras click. |
| **C2** | Login Register | **Password strength**: Sin indicador de fortaleza | Agregar barra visual: rojo < 8 chars, amarillo 8-11, verde ≥ 12 + símbolos. |
| **C3** | Dashboard | **Empty state**: Sin diseño para usuario sin datos sincronizados | Ilustración + "Conecta tu cuenta del SAES para ver tu progreso" + CTA "Sincronizar ahora". |

### 11.2 Medios (mejoran significativamente la experiencia)

| # | Pantalla | Regla UX violada | Corrección |
|---|----------|-----------------|------------|
| **M1** | Generador | **Visual hierarchy**: Badges de cupo usan texto ("Alto", "Medio") | Usar badges de color SEMÁFORO: 🟢 Disponible (≥10), 🟡 Bajo (5-9), 🟠 Crítico (1-4), 🔴 Lleno (0). Con tooltip mostrando el número exacto al hover. |
| **M2** | Generador | **Filtros incompletos**: Faltan Turno y Profesor | Agregar dropdown Turno (Matutino/Vespertino/Mixto) y multiselect Profesor (opcional). |
| **M3** | Generador | **Criterios incompletos**: Solo 2 de 3 | Agregar "Compacto (menos horas libres)" junto con "Días libres" y "Entrar tarde". |
| **M4** | Dashboard | **Missing CTA**: Sin camino desde Pendientes al Generador | Botón "Generar horario con estas materias" al final de la sección Pendientes. Navega al generador con las materias preseleccionadas. |
| **M5** | Dashboard | **Sync timestamp**: Solo dice "Al día", no cuándo | Agregar: "🟢 Sincronizado hace 5 min" o "🟡 Última sincronización: ayer". |

### 11.3 Claymorphism (fidelidad visual al estilo)

| # | Regla Claymorphism (UX Pro Max) | Especificación exacta |
|---|-------------------------------|----------------------|
| **CL1** | Fondo NUNCA blanco puro | `background-color: #F4F1FA` (lavanda frío) en TODA la app. |
| **CL2** | Cards con glass-clay híbrido | `background: rgba(255, 255, 255, 0.7)` + `backdrop-filter: blur(12px)`. |
| **CL3** | Sombras multi-capa | NO usar una sola sombra plana. Usar stack: `box-shadow: 8px 8px 16px rgba(124,58,237,0.08), -4px -4px 12px rgba(255,255,255,0.9), inset 1px 1px 2px rgba(255,255,255,0.8)`. |
| **CL4** | Border radius generoso | Cards: 32px. Botones: 20px. Inputs: 16px. Modals: 40px. |
| **CL5** | Botón primario con gradiente | `background: linear-gradient(135deg, #A78BFA, #7C3AED)`, NO color sólido. |
| **CL6** | Presionar = squish | `transform: scale(0.92)` + `transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1)` en `:active`. |
| **CL7** | Tipografía | Headings: Inter Bold (o Nunito Black para más personalidad). Body: Inter Regular. Mono: JetBrains Mono para datos (claves, calificaciones, números). |

### 11.4 Accesibilidad (obligatorio antes de producción)

| # | Regla | Verificación |
|---|-------|-------------|
| **A11y-1** | Contraste 4.5:1 mínimo | `#1E1B4B` (texto) sobre `#F4F1FA` (fondo) = **15.2:1** ✅. Verificar también texto secundario `#6B7280` → debe ser ≥ 4.5:1 sobre fondos claros. |
| **A11y-2** | Focus rings visibles | TODO elemento interactivo debe tener `ring-2 ring-[#7C3AED] ring-offset-2` en `:focus-visible`. NUNCA `outline: none` sin alternativa. |
| **A11y-3** | Labels en inputs | Todo `<input>` debe tener `<label htmlFor>` asociado. Placeholder NUNCA reemplaza label. |
| **A11y-4** | Skip-to-content | Link oculto al inicio: "Saltar al contenido principal". Visible en focus. |
| **A11y-5** | `prefers-reduced-motion` | Envolver animaciones en `@media (prefers-reduced-motion: no-preference)`. |

---

## 12. Resumen de endpoints que consume el frontend (actualizado)
