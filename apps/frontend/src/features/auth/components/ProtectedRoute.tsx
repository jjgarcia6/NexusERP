import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthStore } from "../../../shared/stores/auth.store";
import type { RoleType } from "../types/auth.types";

type ProtectedRouteProps = {
  allowedRoles?: RoleType[];
};

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const accessToken = useAuthStore((state) => state.accessToken);
  const user = useAuthStore((state) => state.user);
  const location = useLocation();

  if (!accessToken) {
    const redirect = encodeURIComponent(location.pathname || "/dashboard");
    return <Navigate to={`/login?redirect=${redirect}`} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
