import { useState } from "react";
import { AlertCircle, CheckCircle2, Eye, EyeOff, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, extractErrorMessage } from "@/lib/api";

interface SaesConnectionWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function SaesConnectionWizard({
  open,
  onOpenChange,
  onSuccess,
}: SaesConnectionWizardProps) {
  const [step, setStep] = useState<"credentials" | "captcha" | "success" | "error">("credentials");
  const [selectedSchool, setSelectedSchool] = useState("escom");
  const [boleta, setBoleta] = useState("");
  const [password, setPassword] = useState("");
  const [captchaSolution, setCaptchaSolution] = useState("");
  const [captchaBase64, setCaptchaBase64] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  // Paso 1: Iniciar vinculación (Obtener Captcha)
  const handleStartLink = async () => {
    if (!boleta || !selectedSchool) return;
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await api.post("/saes/link/start", {
        boleta,
        school: selectedSchool,
      });
      setCaptchaBase64(res.data.captcha_base64);
      setStep("captcha");
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  // Paso 2: Resolver Captcha y enviar contraseña
  const handleCompleteLink = async () => {
    if (!password || !captchaSolution) return;
    setIsLoading(true);
    setErrorMsg("");
    try {
      await api.post("/saes/link/complete", {
        password,
        captcha_solution: captchaSolution,
      });
      // Forzar sincronización académica inicial
      await api.post("/dashboard/sync");
      setStep("success");
      if (onSuccess) onSuccess();
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  // Recargar captcha si expira o es incorrecto
  const handleRefreshCaptcha = async () => {
    setIsLoading(true);
    try {
      const res = await api.post("/saes/link/start", {
        boleta,
        school: selectedSchool,
      });
      setCaptchaBase64(res.data.captcha_base64);
      setCaptchaSolution("");
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setStep("credentials");
    setBoleta("");
    setPassword("");
    setShowPassword(false);
    setCaptchaSolution("");
    setCaptchaBase64("");
    setErrorMsg("");
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(val) => {
        if (!val) reset();
        onOpenChange(val);
      }}
    >
      <DialogContent className="rounded-clay-2xl border-0 bg-white/95 p-6 sm:p-7 shadow-clay-lg backdrop-blur-md max-w-md w-[92vw] sm:w-full mx-auto">
        <DialogHeader className="space-y-1.5 pb-2">
          <DialogTitle className="text-xl font-bold text-clay-text">
            {step === "credentials" && "Vincula tu cuenta SAES"}
            {step === "captcha" && "Verificación de Seguridad"}
            {step === "success" && "¡Conexión Exitosa!"}
            {step === "error" && "Error de Conexión"}
          </DialogTitle>
          <DialogDescription className="text-sm text-clay-text-secondary">
            {step === "credentials" && "Paso 1 de 2: Selecciona tu plantel e ingresa tu boleta."}
            {step === "captcha" && "Paso 2 de 2: Resuelve el captcha para autorizar el acceso."}
            {step === "success" && "Tus materias y calificaciones se han sincronizado correctamente."}
            {step === "error" && "Hubo un problema al conectar con el SAES."}
          </DialogDescription>
        </DialogHeader>

        {/* PASO 1: Datos de la Escuela y Boleta */}
        {step === "credentials" && (
          <div className="space-y-4 pt-1">
            {/* Selector Visual de Plantel */}
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-clay-text flex items-center justify-between">
                <span>Selecciona tu Plantel</span>
                <span className="text-xs text-clay-text-secondary font-normal">IPN</span>
              </Label>
              
              <div className="grid grid-cols-2 gap-3">
                {[
                  {
                    id: "escom",
                    siglas: "ESCOM",
                    nombre: "Escuela Superior de Cómputo",
                    carreras: "ISC · LCD · IIA",
                    icon: "💻",
                  },
                  {
                    id: "esiatec",
                    siglas: "ESIATEC",
                    nombre: "ESIA Tecamachalco",
                    carreras: "Ing. Arquitecto",
                    icon: "🏛️",
                  },
                ].map((s) => {
                  const isSelected = (selectedSchool || "escom") === s.id;
                  return (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => setSelectedSchool(s.id)}
                      className={`relative flex flex-col items-start p-3.5 rounded-2xl text-left transition-all duration-300 ${
                        isSelected
                          ? "bg-white text-clay-text shadow-clay-lg border-2 border-clay-primary -translate-y-0.5"
                          : "bg-clay-surface/40 hover:bg-white/60 text-clay-text-secondary border-2 border-transparent shadow-clay-input hover:shadow-clay"
                      }`}
                    >
                      {isSelected && (
                        <span className="absolute top-2.5 right-2.5 h-2 w-2 rounded-full bg-clay-primary ring-4 ring-clay-primary/20" />
                      )}
                      <div className="text-2xl mb-1.5">{s.icon}</div>
                      <span className={`font-bold text-sm leading-none mb-1 ${isSelected ? "text-clay-primary" : "text-clay-text"}`}>
                        {s.siglas}
                      </span>
                      <span className="text-[11px] text-clay-text-secondary leading-tight line-clamp-1 mb-1.5">
                        {s.nombre}
                      </span>
                      <span className="inline-block text-[9px] font-semibold px-2 py-0.5 rounded-md bg-clay-surface text-clay-text-secondary/80">
                        {s.carreras}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="boleta-input" className="text-sm font-semibold text-clay-text">
                Número de Boleta SAES
              </Label>
              <Input
                id="boleta-input"
                type="text"
                pattern="\d*"
                maxLength={10}
                placeholder="Ej. 2024600001"
                value={boleta}
                onChange={(e) => setBoleta(e.target.value.replace(/\D/g, ""))}
                disabled={isLoading}
                className="h-12 rounded-2xl border-0 bg-[#f4f1fa] px-4 font-mono text-base shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              />
            </div>

            <Button
              onClick={handleStartLink}
              disabled={isLoading || !boleta || boleta.length < 10}
              className="w-full h-12 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.95] transition-all duration-300 disabled:opacity-60 mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Conectando al SAES...
                </>
              ) : (
                "Continuar al Captcha"
              )}
            </Button>
          </div>
        )}

        {/* PASO 2: Resolver Captcha y Contraseña */}
        {step === "captcha" && (
          <div className="space-y-4 pt-1">
            {/* Imagen de Captcha con botón de recarga */}
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-clay-text">
                Código de seguridad del SAES
              </Label>
              <div className="flex items-center justify-between p-2.5 rounded-2xl bg-[#f4f1fa] shadow-clay-input border border-clay-border/20">
                <div className="flex-1 flex items-center justify-center py-1">
                  {captchaBase64 ? (
                    <img
                      src={`data:image/png;base64,${captchaBase64}`}
                      alt="Captcha SAES"
                      className="h-12 object-contain rounded-lg filter drop-shadow-sm select-none"
                    />
                  ) : (
                    <div className="h-12 flex items-center justify-center text-sm text-clay-text-secondary">
                      Cargando captcha...
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleRefreshCaptcha}
                  disabled={isLoading}
                  className="p-2 rounded-xl text-clay-primary bg-white/80 shadow-clay hover:bg-white active:scale-95 disabled:opacity-50 transition-all shrink-0 ml-2"
                  title="Recargar nueva imagen de captcha"
                >
                  <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
                </button>
              </div>
            </div>

            {/* Input Captcha */}
            <div className="space-y-2">
              <Label htmlFor="captcha-solution-input" className="text-sm font-semibold text-clay-text">
                Escribe las letras de la imagen
              </Label>
              <Input
                id="captcha-solution-input"
                type="text"
                autoComplete="off"
                placeholder="Ej. ABCD"
                value={captchaSolution}
                onChange={(e) => setCaptchaSolution(e.target.value.toUpperCase())}
                disabled={isLoading}
                className="h-12 rounded-2xl border-0 bg-[#f4f1fa] px-4 font-mono font-bold tracking-widest text-center uppercase text-lg shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              />
            </div>

            {/* Input Contraseña con Toggle de visibilidad */}
            <div className="space-y-2">
              <Label htmlFor="password-saes-input" className="text-sm font-semibold text-clay-text">
                Contraseña del SAES
              </Label>
              <div className="relative">
                <Input
                  id="password-saes-input"
                  type={showPassword ? "text" : "password"}
                  placeholder="Tu contraseña del SAES"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="h-12 rounded-2xl border-0 bg-[#f4f1fa] pl-4 pr-12 text-sm shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg text-clay-text-secondary hover:text-clay-text hover:bg-clay-surface transition-colors"
                  title={showPassword ? "Ocultar contraseña" : "Ver contraseña"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                variant="outline"
                onClick={() => setStep("credentials")}
                disabled={isLoading}
                className="w-1/3 h-12 rounded-2xl border-clay-border bg-white text-clay-text font-semibold hover:bg-clay-surface active:scale-95 transition-all shadow-clay"
              >
                Atrás
              </Button>
              <Button
                onClick={handleCompleteLink}
                disabled={isLoading || !password || !captchaSolution}
                className="w-2/3 h-12 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.95] transition-all duration-300 disabled:opacity-60"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Vinculando...
                  </>
                ) : (
                  "Vincular cuenta"
                )}
              </Button>
            </div>
          </div>
        )}

        {/* PASO 3: Éxito */}
        {step === "success" && (
          <div className="py-6 text-center space-y-4 pt-2">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 mx-auto shadow-clay">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <p className="font-bold text-lg text-clay-text">¡Cuenta vinculada!</p>
            <p className="text-sm text-clay-text-secondary">
              Tu boleta <span className="font-mono font-medium text-clay-text">{boleta}</span> ha sido conectada. Ya puedes ver tu kárdex y materias pendientes.
            </p>
            <Button
              onClick={() => onOpenChange(false)}
              className="w-full rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.92] transition-all"
            >
              Ir al Dashboard
            </Button>
          </div>
        )}

        {/* PASO 4: Error */}
        {step === "error" && (
          <div className="py-6 text-center space-y-4 pt-2">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600 mx-auto shadow-clay">
              <AlertCircle className="h-10 w-10" />
            </div>
            <p className="font-bold text-lg text-clay-text">No se pudo vincular</p>
            <p className="text-sm text-red-600 max-w-xs mx-auto">
              {errorMsg}
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setStep("credentials")}
                className="flex-1 rounded-2xl border-clay-border bg-white text-clay-text py-6"
              >
                Ajustar boleta
              </Button>
              <Button
                onClick={() => {
                  setStep("captcha");
                  handleRefreshCaptcha();
                }}
                className="flex-1 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-white font-semibold"
              >
                Reintentar
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
