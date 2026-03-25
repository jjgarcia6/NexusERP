import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { useAuth } from "../hooks/useAuth";
import { registerSchema } from "../types/auth.types";
import type { RegisterType } from "../types/auth.types";

export function RegisterForm() {
  const { register: registerUser, isLoading, errorMessage } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterType>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: RegisterType) => {
    await registerUser(data);
  };

  return (
    <form
      className="flex w-full max-w-md flex-col gap-4 rounded-xl border border-slate-300 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
      noValidate
      onSubmit={handleSubmit(onSubmit)}
    >
      <Label className="flex flex-col gap-1">
        Nombre completo
        <Input type="text" placeholder="María Pérez" {...register("full_name")} />
        {errors.full_name ? (
          <span className="text-sm text-red-600 dark:text-red-400">{errors.full_name.message}</span>
        ) : null}
      </Label>

      <Label className="flex flex-col gap-1">
        Correo electrónico
        <Input type="email" placeholder="usuario@empresa.com" {...register("email")} />
        {errors.email ? <span className="text-sm text-red-600 dark:text-red-400">{errors.email.message}</span> : null}
      </Label>

      <Label className="flex flex-col gap-1">
        Contraseña
        <Input type="password" placeholder="••••••••" {...register("password")} />
        {errors.password ? (
          <span className="text-sm text-red-600 dark:text-red-400">{errors.password.message}</span>
        ) : null}
      </Label>

      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      <Button
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? "Creando cuenta..." : "Crear cuenta"}
      </Button>
    </form>
  );
}
