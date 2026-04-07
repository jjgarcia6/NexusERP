import { create } from 'zustand'
import { PaymentMethodType, CartLineType } from '../types/sales.types'

interface CartState {
  lines: CartLineType[]
  customer: string | null
  paymentMethod: PaymentMethodType | null
  addLine: (line: CartLineType) => void
  updateQuantity: (product_id: string, quantity: number) => void
  removeLine: (product_id: string) => void
  setCustomer: (customer: string | null) => void
  setPaymentMethod: (method: PaymentMethodType | null) => void
  clearCart: () => void
}

export const useCartStore = create<CartState>((set) => ({
  lines: [],
  customer: null,
  paymentMethod: null,
  addLine: (line) => {
    set((state) => {
      const existing = state.lines.find(l => l.product_id === line.product_id)
      if (existing) {
        return {
          ...state,
          lines: state.lines.map(l =>
            l.product_id === line.product_id
              ? { ...l, quantity: Math.min(l.quantity + line.quantity, line.available_quantity) }
              : l
          )
        }
      }
      return {
        ...state,
        lines: [
          ...state.lines,
          { ...line, quantity: Math.min(line.quantity, line.available_quantity) }
        ]
      }
    })
  },
  updateQuantity: (product_id, quantity) => {
    set((state) => ({
      ...state,
      lines: state.lines.map(l =>
        l.product_id === product_id
          ? { ...l, quantity: Math.max(1, Math.min(quantity, l.available_quantity)) }
          : l
      )
    }))
  },
  removeLine: (product_id) => {
    set((state) => ({
      ...state,
      lines: state.lines.filter(l => l.product_id !== product_id)
    }))
  },
  setCustomer: (customer) => set({ customer }),
  setPaymentMethod: (method) => set({ paymentMethod: method }),
  clearCart: () => set({ lines: [], customer: null, paymentMethod: null })
}))
