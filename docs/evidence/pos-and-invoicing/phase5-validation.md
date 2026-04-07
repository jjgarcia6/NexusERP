# Evidencia Fase 5 - POS and Invoicing

Fecha: 2026-04-06

## 5.1 Backend tests (`test_sales.py`)

Comando ejecutado:

- `python -m pytest tests/test_sales.py -v`

Resultado:

- `13 passed`
- Casos cubiertos:
  - Calculo de impuestos.
  - Cliente/producto inactivo.
  - Confirmacion con decremento de stock.
  - Fallos de stock y no-mutacion parcial.
  - Secuencial unico concurrente de comprobantes.
  - Fallo de inventario con `503`.
  - Cancelacion y reversion de stock.
  - Preservacion de `invoice_number` al cancelar.
  - Control de roles (`403`) para operaciones restringidas.

## 5.2 Verificacion OCP en `sales/services`

Comandos ejecutados:

- `git diff -- apps/backend/sales/services/`
- `Select-String "stock_level_repository" apps/backend/sales/services/**/*.py`

Resultado:

- Sin acceso directo a `stock_levels` desde `sales/services`.
- No hay import de `stock_level_repository` en `apps/backend/sales/services`.

## 5.3 Frontend tests (`POSScreen.test.tsx`)

Comando ejecutado:

- `npx vitest run src/features/sales/components/POSScreen.test.tsx`

Resultado:

- `5 passed`
- Casos cubiertos:
  - Confirm deshabilitado con carrito vacio.
  - Confirm deshabilitado sin cliente.
  - Confirm deshabilitado con issue de stock.
  - Badge de stock insuficiente visible.
  - `clearCart` tras confirmacion exitosa.

## 5.4 Integracion manual

Estado:

- Pendiente de ejecucion manual en entorno integrado con backend+frontend activos y Atlas disponible.
- Los pasos del checklist de la tarea 5.4 no se pueden certificar solo con pruebas unitarias aisladas.
