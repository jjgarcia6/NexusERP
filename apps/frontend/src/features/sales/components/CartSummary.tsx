import { FC } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card'
import { Separator } from '../../../components/ui/separator'

interface CartSummaryProps {
  subtotalBeforeTax: number
  taxAmount: number
  total: number
}

export const CartSummary: FC<CartSummaryProps> = ({ subtotalBeforeTax, taxAmount, total }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Resumen</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between py-1">
          <span>Subtotal</span>
          <span className="font-mono">${subtotalBeforeTax.toFixed(2)}</span>
        </div>
        <div className="flex justify-between py-1">
          <span>IVA (12%)</span>
          <span className="font-mono">${taxAmount.toFixed(2)}</span>
        </div>
        <Separator className="my-2" />
        <div className="flex justify-between py-1 text-lg font-bold">
          <span>Total</span>
          <span className="font-mono">${total.toFixed(2)}</span>
        </div>
      </CardContent>
    </Card>
  )
}
