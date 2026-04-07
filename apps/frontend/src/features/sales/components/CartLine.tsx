import { FC } from 'react'
import { CartLineType } from '../types/sales.types'

interface CartLineProps {
  line: CartLineType
  onQuantityChange: (quantity: number) => void
  onRemove: () => void
}

export const CartLine: FC<CartLineProps> = ({ line, onQuantityChange, onRemove }) => {
  return (
    <div className="flex items-center gap-4 p-2 border-b dark:border-gray-700">
      <div className="flex-1">
        <div className="font-medium">{line.product_name}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">${line.unit_price.toFixed(2)} c/u</div>
      </div>
      <input
        type="number"
        min={1}
        max={line.available_quantity}
        value={line.quantity}
        onChange={e => onQuantityChange(Number(e.target.value))}
        className="w-16 border rounded px-2 py-1 text-right dark:bg-gray-800 dark:border-gray-600"
        title="Cantidad"
        placeholder="Cantidad"
      />
      <div className="w-24 text-right font-mono">{(line.unit_price * line.quantity).toFixed(2)}</div>
      {line.quantity > line.available_quantity && (
        <span className="ml-2 rounded bg-red-200 px-2 py-1 text-xs font-semibold text-red-900 dark:bg-red-800 dark:text-red-100">
          Stock insuficiente
        </span>
      )}
      <button
        onClick={onRemove}
        className="ml-2 text-red-500 hover:text-red-700 dark:text-red-300 dark:hover:text-red-500 text-xl font-bold"
        aria-label="Eliminar línea"
      >
        ×
      </button>
    </div>
  )
}
