/** Cliente HTTP centralizado para la API de Tetring v2.
 *
 * Todos los interceptores y tipos de respuesta se definen aquí para mantener
 * consistencia en el manejo de errores y autenticación.
 */
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

import { useAuthStore } from "@/stores/auth-store";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export interface ApiError {
  detail: string | { loc: (string | number)[]; msg: string; type: string }[];
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface CitaReinscripcionInfo {
  fecha?: string | null;
  hora?: string | null;
  lugar?: string | null;
  estatus?: string | null;
  creditos_maximos?: string | null;
  creditos_minimos?: string | null;
  mensaje?: string | null;
}

export interface DashboardSummaryResponse {
  cursadas: number;
  promedio: number;
  pendientes: number;
  obligatorias_pendientes?: number;
  optativas_pendientes?: number;
  cita?: CitaReinscripcionInfo | null;
  last_sync_at?: string | null;
}

export interface KardexEntryResponse {
  clave: string;
  asignatura: string;
  calificacion: number;
  periodo: string;
}

export interface PendingSubjectResponse {
  clave: string;
  nombre: string;
  creditos: number;
  semestre: number;
  tipo?: string;
}

export interface SaesProfileResponse {
  boleta: string;
  escuela: string;
  escuela_nombre?: string;
}

export interface SyncResponse {
  kardex_count: number;
  curriculum_count: number;
  schedule_count: number;
}

export interface ScheduleGroupResponse {
  grupo: string;
  asignatura: string;
  profesor: string;
  horario: string;
  cupo: number;
  disponibles?: number;
}

export interface ScheduleResultResponse {
  id: string;
  rank: number;
  label: string;
  free_hours: number;
  groups: ScheduleGroupResponse[];
}

export interface GenerateScheduleRequest {
  subject_claves: string[];
  turno?: string;
  scoring?: string[];
  exclude_professors?: string[];
  pinned_groups?: Record<string, string>;
  filters?: {
    start_min?: number;
    start_max?: number;
  };
  max_results?: number;
}

export type ProfessorResponse = string[];


export interface SaveScheduleRequest {
  name: string;
  groups: ScheduleGroupResponse[];
}

export interface SavedScheduleResponse {
  id: string;
  name: string;
  is_favorite: boolean;
  created_at: string;
  groups: OptionItemResponse[];
}

export interface OptionItemResponse {
  grupo: string;
  clave: string;
  asignatura: string;
  profesor: string;
  edificio?: string | null;
  aula?: string | null;
  lunes?: string | null;
  martes?: string | null;
  miercoles?: string | null;
  jueves?: string | null;
  viernes?: string | null;
}

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(callback: (token: string) => void): void {
  refreshSubscribers.push(callback);
}

function onTokenRefreshed(token: string): void {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => {
    const url = response.config.url || "";
    if (url.includes("/saes/link/complete") || url.includes("/dashboard/sync") || url.includes("/saes/profile")) {
      useAuthStore.getState().setSaesExpired(false);
    }
    return response;
  },
  async (error: AxiosError<ApiError>) => {
    const detail = error.response?.data?.detail;
    const url = error.config?.url || "";
    
    if (
      detail === "SESSION_EXPIRED" || 
      (typeof detail === "string" && detail.includes("SESSION_EXPIRED")) ||
      (error.response?.status === 401 && (url.includes("/saes/") || url.includes("/dashboard/sync") || url.includes("/schedules/")))
    ) {
      useAuthStore.getState().setSaesExpired(true);
    }

    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (!originalRequest) {
      return Promise.reject(error);
    }

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = useAuthStore.getState().refreshToken;
    if (!refreshToken) {
      useAuthStore.getState().logout();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token) => {
          if (!token) {
            reject(error);
            return;
          }
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await api.post<TokenResponse>("/auth/refresh", {
        refresh_token: refreshToken,
      });

      useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
      onTokenRefreshed(data.access_token);
      originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      return api(originalRequest);
    } catch (refreshError) {
      onTokenRefreshed("");
      useAuthStore.getState().logout();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg).join(". ");
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Algo salió mal. Intenta de nuevo.";
}
