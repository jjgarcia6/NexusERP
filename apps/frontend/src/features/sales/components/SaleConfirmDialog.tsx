import { FC, useState } from 'react'
import { CartLineType, PaymentMethodType } from '../types/sales.types'
import { useSales } from '../hooks/useSales'
import { useCartStore } from '../stores/cart.store'

interface SaleConfirmDialogProps {
  cart: {
    lines: CartLineType[]
    customer: string | null
    paymentMethod: PaymentMethodType | null
    subtotalBeforeTax: number
    taxAmount: number
    total: number
  }
  onConfirm: () => void
}

export const SaleConfirmDialog: FC<SaleConfirmDialogProps> = ({ cart, onConfirm }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { createSale, confirmSale } = useSales()
  const clearCart = useCartStore(s => s.clearCart)
  const setPaymentMethod = useCartStore(s => s.setPaymentMethod)

  const formatStockError = (candidate: unknown): string => {
    const maybeError = candidate as {
      response?: {
        data?: {
          detail?: unknown
        }
      }
      message?: string
    }

    const detail = maybeError.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }

    if (detail && typeof detail === 'object') {
      const detailObject = detail as {
        error?: string
        products?: Array<{ product_id?: string; available?: number; requested?: number }>
      }
      const firstProduct = detailObject.products?.[0]
      if (firstProduct?.product_id) {
        return `Stock insuficiente para ${firstProduct.product_id}: disponible ${firstProduct.available ?? 0}, solicitado ${firstProduct.requested ?? 0}`
      }
      if (detailObject.error) {
        return detailObject.error
      }
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const firstError = detail[0] as { msg?: string }
      if (typeof firstError?.msg === 'string' && firstError.msg.length > 0) {
        return firstError.msg
      }
      return 'Datos inválidos para crear la venta'
    }

    if (typeof maybeError.message === 'string' && maybeError.message.length > 0) {
      return maybeError.message
    }

    return 'Error al confirmar venta'
  }

  const handleConfirm = async () => {
    setLoading(true)
    setError(null)
    try {
      const sale = await createSale({
        customer_id: cart.customer!,
        payment_method: cart.paymentMethod!,
        lines: cart.lines.map(l => ({ product_id: l.product_id, quantity: l.quantity }))
      })
      await confirmSale(sale.id)
      clearCart()
      onConfirm()
    } catch (error: unknown) {
      setError(formatStockError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white dark:bg-gray-900 rounded shadow-md w-full max-w-md mx-auto">
      <h2 className="text-lg font-bold mb-4">Confirmar venta</h2>
      <div className="mb-2">Cliente: <span className="font-semibold">{cart.customer}</span></div>
      <div className="mb-2">Método de pago:
        <select
          aria-label="Metodo de pago"
          title="Metodo de pago"
          value={cart.paymentMethod || ''}
          onChange={e => setPaymentMethod(e.target.value as PaymentMethodType)}
          className="ml-2 border rounded px-2 py-1 dark:bg-gray-800 dark:border-gray-600"
        >
          <option value="">Selecciona</option>
          <option value="cash">Efectivo</option>
          <option value="card">Tarjeta</option>
          <option value="transfer">Transferencia</option>
        </select>
      </div>
      <div className="mb-2">Totales: <span className="font-mono">${cart.total.toFixed(2)}</span></div>
      <ul className="mb-4">
        {cart.lines.map(line => (
          <li key={line.product_id} className="flex justify-between text-sm">
            <span>{line.product_name} × {line.quantity}</span>
            <span>${(line.unit_price * line.quantity).toFixed(2)}</span>
          </li>
        ))}
      </ul>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <button
        onClick={handleConfirm}
        disabled={loading}
        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Procesando...' : 'Confirmar'}
      </button>
    </div>
  )
}
