import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { useAuth } from "../hooks/useAuth";
import { loginSchema } from "../types/auth.types";
import type { LoginType } from "../types/auth.types";

export function LoginForm() {
  const { login, isLoading, errorMessage } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginType>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginType) => {
    await login(data);
  };

  return (
    <form
      className="flex w-full max-w-md flex-col gap-4 rounded-xl border border-slate-300 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
      noValidate
      onSubmit={handleSubmit(onSubmit)}
    >
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
        {isLoading ? "Ingresando..." : "Ingresar"}
      </Button>
    </form>
  );
}
