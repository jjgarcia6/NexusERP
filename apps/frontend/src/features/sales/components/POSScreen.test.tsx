import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { POSScreen } from './POSScreen'

const clearCartMock = vi.fn()
const setPaymentMethodMock = vi.fn()
const createSaleMock = vi.fn()
const confirmSaleMock = vi.fn()

vi.mock('../../catalog/hooks/useProducts', () => ({
  useProducts: () => ({ products: [], isLoading: false })
}))

vi.mock('../../customers', () => ({
  CustomerSelector: ({ onSelect }: { onSelect: (customer: { id: string }) => void }) => (
    <button type="button" onClick={() => onSelect({ id: 'cust-1' })}>Seleccionar cliente</button>
  )
}))

vi.mock('../hooks/useSales', () => ({
  useSales: () => ({
    createSale: createSaleMock,
    confirmSale: confirmSaleMock
  })
}))

vi.mock('../stores/cart.store', () => ({
  useCartStore: (selector: (state: { clearCart: () => void; setPaymentMethod: (value: string | null) => void }) => unknown) =>
    selector({
      clearCart: clearCartMock,
      setPaymentMethod: setPaymentMethodMock
    })
}))

const useCartMock = vi.fn()

vi.mock('../hooks/useCart', () => ({
  useCart: () => useCartMock()
}))

function buildCartState(overrides: Record<string, unknown> = {}) {
  return {
    lines: [
      {
        product_id: 'prd-1',
        product_name: 'Producto 1',
        quantity: 1,
        available_quantity: 10,
        unit_price: 12.5
      }
    ],
    customer: 'cust-1',
    paymentMethod: 'cash',
    hasStockIssues: false,
    subtotalBeforeTax: 12.5,
    taxAmount: 1.5,
    total: 14,
    updateQuantity: vi.fn(),
    removeLine: vi.fn(),
    setPaymentMethod: vi.fn(),
    clearCart: vi.fn(),
    ...overrides
  }
}

describe('POSScreen', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    vi.clearAllMocks()
    createSaleMock.mockResolvedValue({ id: 'sale-1' })
    confirmSaleMock.mockResolvedValue({ id: 'sale-1', status: 'confirmed' })
  })

  it('should_disable_confirm_button_when_cart_is_empty', () => {
    useCartMock.mockReturnValue(buildCartState({ lines: [] }))

    render(<POSScreen />)

    expect(screen.getByRole('button', { name: 'Confirmar venta' })).toBeDisabled()
  })

  it('should_disable_confirm_button_when_no_customer_selected', () => {
    useCartMock.mockReturnValue(buildCartState({ customer: null }))

    render(<POSScreen />)

    expect(screen.getByRole('button', { name: 'Confirmar venta' })).toBeDisabled()
  })

  it('should_disable_confirm_button_when_stock_issue_exists', () => {
    useCartMock.mockReturnValue(buildCartState({ hasStockIssues: true }))

    render(<POSScreen />)

    expect(screen.getByRole('button', { name: 'Confirmar venta' })).toBeDisabled()
  })

  it('should_show_stock_warning_badge_on_cart_line_when_quantity_exceeds_stock', () => {
    useCartMock.mockReturnValue(
      buildCartState({
        lines: [
          {
            product_id: 'prd-1',
            product_name: 'Producto 1',
            quantity: 5,
            available_quantity: 2,
            unit_price: 12.5
          }
        ]
      })
    )

    render(<POSScreen />)

    expect(screen.getByText('Stock insuficiente')).toBeInTheDocument()
  })

  it('should_clear_cart_after_successful_confirmation', async () => {
    useCartMock.mockReturnValue(buildCartState())

    render(<POSScreen />)

    fireEvent.click(screen.getByRole('button', { name: 'Confirmar venta' }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar' }))

    await waitFor(() => {
      expect(createSaleMock).toHaveBeenCalledTimes(1)
      expect(confirmSaleMock).toHaveBeenCalledTimes(1)
      expect(clearCartMock).toHaveBeenCalledTimes(1)
    })
  })
})
