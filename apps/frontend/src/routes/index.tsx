import { lazy, Suspense } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";

import { MainLayout } from "../components/layouts/MainLayout";
import { ProtectedRoute } from "../features/auth";

const LoginPage = lazy(() =>
  import("../pages/LoginPage").then((module) => ({
    default: module.LoginPage,
  }))
);

const RegisterPage = lazy(() =>
  import("../pages/RegisterPage").then((module) => ({
    default: module.RegisterPage,
  }))
);

const DashboardPage = lazy(() =>
  import("../pages/DashboardPage").then((module) => ({
    default: module.DashboardPage,
  }))
);

const ProductsPage = lazy(() =>
  import("../pages/ProductsPage").then((module) => ({
    default: module.ProductsPage,
  }))
);

const CategoriesPage = lazy(() =>
  import("../pages/CategoriesPage").then((module) => ({
    default: module.CategoriesPage,
  }))
);

const SuppliersPage = lazy(() =>
  import("../pages/SuppliersPage").then((module) => ({
    default: module.SuppliersPage,
  }))
);

const PurchasesPage = lazy(() =>
  import("../pages/PurchasesPage").then((module) => ({
    default: module.PurchasesPage,
  }))
);

const InventoryPage = lazy(() =>
  import("../pages/InventoryPage").then((module) => ({
    default: module.InventoryPage,
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
        path: "register",
        element: (
          <Suspense fallback={<div className="p-6">Cargando...</div>}>
            <RegisterPage />
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
          {
            path: "products",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <ProductsPage />
              </Suspense>
            ),
          },
          {
            path: "products/:productId",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <ProductsPage />
              </Suspense>
            ),
          },
          {
            path: "categories",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <CategoriesPage />
              </Suspense>
            ),
          },
          {
            path: "suppliers",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <SuppliersPage />
              </Suspense>
            ),
          },
          {
            path: "purchases",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <PurchasesPage />
              </Suspense>
            ),
          },
          {
            path: "purchases/:orderId",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <PurchasesPage />
              </Suspense>
            ),
          },
          {
            path: "inventory",
            element: (
              <Suspense fallback={<div className="p-6">Cargando...</div>}>
                <InventoryPage />
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
