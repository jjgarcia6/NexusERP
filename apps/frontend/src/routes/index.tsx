import { lazy, Suspense } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";

import { MainLayout } from "../components/custom/layouts/MainLayout";
import { ProtectedRoute } from "../features/auth";

const LoginPage = lazy(() =>
  import("../pages/LoginPage").then((module) => ({
    default: module.LoginPage,
  }))
);

const DashboardPage = lazy(() =>
  import("../pages/DashboardPage").then((module) => ({
    default: module.DashboardPage,
  }))
);

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        path: "login",
        element: (
          <Suspense fallback={<div className="p-6">Cargando...</div>}>
            <LoginPage />
          </Suspense>
        ),
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: "dashboard",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <DashboardPage />
              </Suspense>
            ),
          },
        ],
      },
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
    ],
  },
]);
