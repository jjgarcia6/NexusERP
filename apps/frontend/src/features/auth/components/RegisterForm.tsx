import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Input } from "../../../components/ui/input";
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
      <label className="flex flex-col gap-1 text-sm font-medium text-slate-700 dark:text-slate-200">
        Nombre completo
        <Input type="text" placeholder="María Pérez" {...register("full_name")} />
        {errors.full_name ? (
          <span className="text-sm text-red-600 dark:text-red-400">{errors.full_name.message}</span>
        ) : null}
      </label>

      <label className="flex flex-col gap-1 text-sm font-medium text-slate-700 dark:text-slate-200">
        Correo electrónico
        <Input type="email" placeholder="usuario@empresa.com" {...register("email")} />
        {errors.email ? <span className="text-sm text-red-600 dark:text-red-400">{errors.email.message}</span> : null}
      </label>

      <label className="flex flex-col gap-1 text-sm font-medium text-slate-700 dark:text-slate-200">
        Contraseña
        <Input type="password" placeholder="••••••••" {...register("password")} />
        {errors.password ? (
          <span className="text-sm text-red-600 dark:text-red-400">{errors.password.message}</span>
        ) : null}
      </label>

      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      <button
        type="submit"
        disabled={isLoading}
        className="rounded-md bg-slate-900 px-4 py-2 font-medium text-white transition hover:bg-slate-800 disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200"
      >
        {isLoading ? "Creando cuenta..." : "Crear cuenta"}
      </button>
    </form>
  );
}
