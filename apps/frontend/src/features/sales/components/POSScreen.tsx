import { FC, useEffect, useMemo, useState } from 'react'
import { CustomerSelector } from '../../customers'
import { useProducts } from '../../catalog/hooks/useProducts'
import apiClient from '../../../shared/api/client'
import { useCart } from '../hooks/useCart'
import { PaymentMethodType } from '../types/sales.types'
import { CartLine } from './CartLine'
import { CartSummary } from './CartSummary'
import { SaleConfirmDialog } from './SaleConfirmDialog'

function hasSameStockMap(a: Record<string, number>, b: Record<string, number>) {
  const aKeys = Object.keys(a)
  const bKeys = Object.keys(b)

  if (aKeys.length !== bKeys.length) {
    return false
  }

  return aKeys.every((key) => a[key] === b[key])
}

export const POSScreen: FC = () => {
  const {
    lines,
    customer,
    paymentMethod,
    hasStockIssues,
    subtotalBeforeTax,
    taxAmount,
    total,
    addProduct,
    updateQuantity,
    removeLine,
    setCustomer,
    setPaymentMethod,
    clearCart
  } = useCart()
  const [search, setSearch] = useState('')
  const [stockByProduct, setStockByProduct] = useState<Record<string, number>>({})
  const [showConfirm, setShowConfirm] = useState(false)
  const { products, isLoading: productsLoading } = useProducts({
    search: search.trim().length >= 2 ? search : undefined,
    skip: 0,
    limit: 10
  })

  const visibleProducts = useMemo(
    () => products.filter(p => p.is_active).slice(0, 5),
    [products]
  )

  const visibleProductIdsKey = useMemo(
    () => visibleProducts.map((product) => product.id).join('|'),
    [visibleProducts]
  )

  useEffect(() => {
    let cancelled = false

    const loadStocks = async () => {
      if (visibleProducts.length === 0) {
        setStockByProduct((previous) => (Object.keys(previous).length === 0 ? previous : {}))
        return
      }

      const pairs = await Promise.all(
        visibleProducts.map(async (product) => {
          try {
            const response = await apiClient.get(`/inventory/stock/${product.id}`)
            const availableQuantity = Number(response.data?.available_quantity ?? 0)
            return [product.id, Number.isNaN(availableQuantity) ? 0 : availableQuantity] as const
          } catch {
            return [product.id, 0] as const
          }
        })
      )

      if (!cancelled) {
        const nextStockByProduct = Object.fromEntries(pairs)
        setStockByProduct((previous) =>
          hasSameStockMap(previous, nextStockByProduct) ? previous : nextStockByProduct
        )
      }
    }

    void loadStocks()
    return () => {
      cancelled = true
    }
  }, [visibleProducts, visibleProductIdsKey])

  const showResults = search.trim().length >= 2

  const handleSelectProduct = async (product: { id: string; name: string; price: number }) => {
    await addProduct({
      product_id: product.id,
      product_name: product.name,
      unit_price: Number(product.price),
      quantity: 1
    })
    setSearch('')
  }

  return (
    <div className="flex flex-col md:flex-row gap-6">
      {/* Columna izquierda: búsqueda y líneas */}
      <div className="flex-1">
        <div className="relative mb-4">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar producto por nombre"
            className="w-full border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-600"
          />
          {showResults && (
            <div className="absolute z-20 mt-1 max-h-72 w-full overflow-y-auto rounded border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
              {productsLoading ? (
                <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-300">Buscando...</div>
              ) : visibleProducts.length === 0 ? (
                <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-300">Sin resultados.</div>
              ) : (
                visibleProducts.map((product) => {
                  const available = stockByProduct[product.id] ?? 0
                  return (
                    <button
                      key={product.id}
                      type="button"
                      onClick={() => void handleSelectProduct(product)}
                      className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-800"
                    >
                      <span className="font-medium">{product.name}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        ${Number(product.price).toFixed(2)} | Stock: {available}
                      </span>
                    </button>
                  )
                })
              )}
            </div>
          )}
        </div>
        <div className="mb-4">Tabla de líneas:</div>
        {lines.map(line => (
          <CartLine
            key={line.product_id}
            line={line}
            onQuantityChange={q => updateQuantity(line.product_id, q)}
            onRemove={() => removeLine(line.product_id)}
          />
        ))}
      </div>
      {/* Columna derecha: resumen, cliente, pago */}
      <div className="w-full md:w-96">
        <CustomerSelector onSelect={(customerResult) => setCustomer(customerResult.id)} />
        <CartSummary subtotalBeforeTax={subtotalBeforeTax} taxAmount={taxAmount} total={total} />
        <div className="my-2">
          <select
            aria-label="Metodo de pago"
            title="Metodo de pago"
            value={paymentMethod || ''}
            onChange={e => setPaymentMethod(e.target.value as PaymentMethodType)}
            className="w-full border rounded px-2 py-1 dark:bg-gray-800 dark:border-gray-600"
          >
            <option value="">Método de pago</option>
            <option value="cash">Efectivo</option>
            <option value="card">Tarjeta</option>
            <option value="transfer">Transferencia</option>
          </select>
        </div>
        <button
          className="w-full py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          onClick={() => setShowConfirm(true)}
          disabled={lines.length === 0 || !customer || hasStockIssues}
        >
          Confirmar venta
        </button>
        <button
          className="w-full py-2 mt-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded"
          onClick={clearCart}
        >
          Limpiar carrito
        </button>
        {showConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 p-4 rounded shadow-lg">
              <SaleConfirmDialog
                cart={{
                  lines,
                  customer,
                  paymentMethod,
                  subtotalBeforeTax,
                  taxAmount,
                  total
                }}
                onConfirm={() => setShowConfirm(false)}
              />
              <button
                onClick={() => setShowConfirm(false)}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
              >
                Cerrar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
