import { useCallback, useMemo } from 'react'
import { useCartStore } from '../stores/cart.store'
import { CartLineType } from '../types/sales.types'
import apiClient from '../../../shared/api/client'

export function useCart() {
  const {
    lines,
    customer,
    paymentMethod,
    addLine,
    updateQuantity,
    removeLine,
    setCustomer,
    setPaymentMethod,
    clearCart
  } = useCartStore()

  // Consulta stock actual de un producto
  const fetchAvailableStock = useCallback(async (product_id: string) => {
    const response = await apiClient.get(`/inventory/stock/${product_id}`)
    const availableQuantity = response.data?.available_quantity
    if (typeof availableQuantity !== 'number') {
      throw new Error('Respuesta de stock invalida')
    }
    return availableQuantity
  }, [])

  // Añadir producto consultando stock
  const addProduct = useCallback(async (product: Omit<CartLineType, 'available_quantity'>) => {
    const available_quantity = await fetchAvailableStock(product.product_id)
    addLine({ ...product, available_quantity })
  }, [addLine, fetchAvailableStock])

  // Calcula si hay líneas con problemas de stock
  const hasStockIssues = useMemo(() =>
    lines.some(l => l.quantity > l.available_quantity),
    [lines]
  )

  // Cálculos de totales
  const subtotalBeforeTax = useMemo(() =>
    lines.reduce((sum, l) => sum + l.quantity * l.unit_price, 0),
    [lines]
  )
  const taxAmount = useMemo(() => subtotalBeforeTax * 0.12, [subtotalBeforeTax])
  const total = useMemo(() => subtotalBeforeTax + taxAmount, [subtotalBeforeTax, taxAmount])

  return {
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
  }
}
