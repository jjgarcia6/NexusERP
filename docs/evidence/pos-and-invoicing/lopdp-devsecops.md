# Evidencia LOPDP y DevSecOps - POS and Invoicing

Fecha: 2026-04-06

## Verificaciones realizadas

- `customer_name` y `customer_identification` se usan para persistencia historica y respuesta de negocio, sin trazas de logging en el modulo de ventas.
- No existe logging del body de `POST /sales` en router o servicio de ventas.
- El backend no implementa middleware custom que registre `request.body()` para ventas.
- El control de acceso por rol queda restringido en rutas de ventas:
  - Crear/confirmar: `admin`, `vendedor`.
  - Cancelar: `admin`.
  - Listar/detalle: `admin`, `vendedor`, `bodeguero`.

## Evidencia tecnica (comandos)

- Ruff sales: `python -m ruff check apps/backend/sales/`
- Ruff format check sales: `python -m ruff format --check apps/backend/sales/`
- Mypy sales strict: `python -m mypy apps/backend/sales/ --strict`
- Bandit sales: `python -m bandit -r apps/backend/sales/ -ll`
- Mypy inventory strict: `python -m mypy apps/backend/inventory/ --strict`
- ESLint sales frontend: `npx eslint src/features/sales/ --max-warnings=0`
- Detect secrets baseline: `python -m detect_secrets scan --baseline .secrets.baseline`

## Nota de cumplimiento

Este cambio desnormaliza PII historica del cliente (nombre e identificacion) en ventas bajo LOPDP.
Medidas aplicadas:

- Exclusion de logs sensibles (sin logging de body ni trazas de PII en ventas).
- Acceso restringido por rol.
- Datos de comprobante inmutables post-confirmacion (incluyendo identificacion historica y numero de comprobante generado en servidor).
