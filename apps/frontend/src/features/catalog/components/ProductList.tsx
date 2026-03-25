import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select } from "../../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import apiClient from "../../../shared/api/client";
import { useAuth } from "../../auth";
import { useCategories } from "../hooks/useCategories";
import { useProducts } from "../hooks/useProducts";
import { productSchema, type ProductRequestType, type ProductType } from "../types/catalog.types";
import { ProductCard } from "./ProductCard";
import { ProductForm } from "./ProductForm";

const PAGE_SIZE = 20;

export function ProductList() {
  const navigate = useNavigate();
  const { productId } = useParams<{ productId: string }>();
  const { isAdmin } = useAuth();
  const { categories, isLoading: categoriesLoading } = useCategories();
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [skip, setSkip] = useState(0);
  const [formOpen, setFormOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ProductType | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
      setSkip(0);
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [searchInput]);

  const queryParams = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      category_id: selectedCategory || undefined,
      skip,
      limit: PAGE_SIZE,
    }),
    [debouncedSearch, selectedCategory, skip]
  );

  const { products, total, isLoading, createProduct, updateProduct } = useProducts(queryParams);

  const productDetailQuery = useQuery({
    queryKey: ["product-detail", productId],
    enabled: Boolean(productId),
    queryFn: async () => {
      const response = await apiClient.get(`/products/${productId}`);
      return productSchema.parse(response.data);
    },
  });

  async function handleSaveProduct(payload: ProductRequestType) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      if (editingProduct) {
        await updateProduct({ productId: editingProduct.id, payload });
      } else {
        await createProduct(payload);
      }
      setFormOpen(false);
      setEditingProduct(null);
    } catch {
      setErrorMessage("No fue posible guardar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeactivate(product: ProductType) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await updateProduct({
        productId: product.id,
        payload: { is_active: false },
      });
    } catch {
      setErrorMessage("No fue posible desactivar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (productId) {
    return (
      <section className="space-y-4">
        <Button
          type="button"
          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
          onClick={() => navigate("/products")}
        >
          Volver al listado
        </Button>
        {productDetailQuery.isLoading ? (
          <p className="text-sm text-slate-600 dark:text-slate-300">Cargando producto...</p>
        ) : productDetailQuery.data ? (
          <ProductCard product={productDetailQuery.data} />
        ) : (
          <p className="text-sm text-red-600 dark:text-red-400">No se pudo cargar el detalle del producto.</p>
        )}
      </section>
    );
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Productos</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">Busca, filtra y administra el catálogo de productos.</p>
        </div>
        {isAdmin ? (
          <Button
            type="button"
            onClick={() => {
              setEditingProduct(null);
              setFormOpen(true);
            }}
          >
            Nuevo producto
          </Button>
        ) : null}
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Label className="flex flex-col gap-2">
          Buscar
          <Input
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Buscar por nombre..."
          />
        </Label>

        <Label className="flex flex-col gap-2">
          Categoría
          <Select
            value={selectedCategory}
            onChange={(event) => {
              setSelectedCategory(event.target.value);
              setSkip(0);
            }}
            disabled={categoriesLoading}
          >
            <option value="">Todas</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Select>
        </Label>
      </div>

      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando productos...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Precio</TableHead>
                {isAdmin ? <TableHead>Costo</TableHead> : null}
                <TableHead>Categoría</TableHead>
                <TableHead>Estado</TableHead>
                {isAdmin ? <TableHead>Acciones</TableHead> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id} className="cursor-pointer" onClick={() => navigate(`/products/${product.id}`)}>
                  <TableCell className="font-medium">{product.name}</TableCell>
                  <TableCell>{product.sku ?? "Sin SKU"}</TableCell>
                  <TableCell>${product.price.toFixed(2)}</TableCell>
                  {isAdmin ? <TableCell>{product.cost !== null && product.cost !== undefined ? `$${product.cost.toFixed(2)}` : "-"}</TableCell> : null}
                  <TableCell>{product.category_name}</TableCell>
                  <TableCell>{product.is_active ? "Activo" : "Inactivo"}</TableCell>
                  {isAdmin ? (
                    <TableCell onClick={(event) => event.stopPropagation()}>
                      <div className="flex gap-2">
                        <Button
                          type="button"
                          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                          onClick={() => {
                            setEditingProduct(product);
                            setFormOpen(true);
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          type="button"
                          className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                          disabled={isSubmitting}
                          onClick={() => {
                            void handleDeactivate(product);
                          }}
                        >
                          Desactivar
                        </Button>
                      </div>
                    </TableCell>
                  ) : null}
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between pt-2">
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Mostrando {products.length} de {total} productos
            </p>
            <div className="flex gap-2">
              <Button
                type="button"
                className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                onClick={() => setSkip((prev) => Math.max(prev - PAGE_SIZE, 0))}
                disabled={skip === 0}
              >
                Anterior
              </Button>
              <Button
                type="button"
                onClick={() => setSkip((prev) => prev + PAGE_SIZE)}
                disabled={skip + PAGE_SIZE >= total}
              >
                Siguiente
              </Button>
            </div>
          </div>
        </>
      )}

      <ProductForm
        open={formOpen}
        onOpenChange={(next) => {
          setFormOpen(next);
          if (!next) {
            setEditingProduct(null);
          }
        }}
        initialValues={editingProduct}
        categories={categories}
        isAdmin={isAdmin}
        isPending={isSubmitting}
        onSubmitProduct={handleSaveProduct}
      />
    </section>
  );
}
