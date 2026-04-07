import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { TopCustomerType, TopProductType } from "../types/reports.types";

type DashboardTopListsProps = {
  topProducts: TopProductType[];
  topCustomers: TopCustomerType[];
};

function formatMoney(value: number): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

export function DashboardTopLists({ topProducts, topCustomers }: DashboardTopListsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Top productos</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>Producto</TableHead>
                <TableHead>Unidades</TableHead>
                <TableHead>Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {topProducts.map((item, index) => (
                <TableRow key={`${item.product_id}-${index}`}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{item.product_name}</TableCell>
                  <TableCell>{item.total_quantity}</TableCell>
                  <TableCell>{formatMoney(item.total_amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {topCustomers.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top clientes</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>#</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Identificación</TableHead>
                  <TableHead>Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {topCustomers.map((item, index) => (
                  <TableRow key={`${item.customer_name}-${index}`}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.customer_name}</TableCell>
                    <TableCell>{item.identification_masked}</TableCell>
                    <TableCell>{formatMoney(item.total_amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
