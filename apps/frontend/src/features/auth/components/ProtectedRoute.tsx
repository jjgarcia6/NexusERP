import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthStore } from "../../../shared/stores/auth.store";

export function ProtectedRoute() {
  const accessToken = useAuthStore((state) => state.accessToken);
  const location = useLocation();

  if (!accessToken) {
    const redirect = encodeURIComponent(location.pathname || "/dashboard");
    return <Navigate to={`/login?redirect=${redirect}`} replace />;
  }

  return <Outlet />;
}
