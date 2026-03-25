import { Badge } from "../../../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import type { ProductType } from "../types/catalog.types";

type ProductCardProps = {
  product: ProductType;
};

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{product.name}</CardTitle>
        <Badge variant={product.is_active ? "success" : "muted"}>
          {product.is_active ? "Activo" : "Inactivo"}
        </Badge>
      </CardHeader>
      <CardContent>
        <p>
          <strong>SKU:</strong> {product.sku ?? "Sin SKU"}
        </p>
        <p>
          <strong>Precio:</strong> ${product.price.toFixed(2)}
        </p>
        {product.cost !== null && product.cost !== undefined ? (
          <p>
            <strong>Costo:</strong> ${product.cost.toFixed(2)}
          </p>
        ) : null}
        <p>
          <strong>Categoría:</strong> {product.category_name}
        </p>
        <p>
          <strong>Descripción:</strong> {product.description ?? "Sin descripción"}
        </p>
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="mt-3 max-h-64 w-full rounded-md object-cover"
          />
        ) : null}
      </CardContent>
    </Card>
  );
}
