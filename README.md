# NexusERP Monorepo Setup

## Requisitos
1. Docker Desktop instalado y ejecutandose.
2. Python 3.11+ (opcional para ejecucion local fuera de docker).
3. Node.js 20+ (opcional para ejecucion local fuera de docker).
4. Credenciales validas de MongoDB Atlas.

## Setup Rapido
1. Copiar `apps/backend/.env.example` a `apps/backend/.env`.
2. Completar `MONGODB_URL`, `MONGODB_DB_NAME`, `SECRET_KEY`.
3. Copiar `apps/frontend/.env.example` a `apps/frontend/.env`.
4. Ajustar `VITE_API_BASE_URL` si es necesario.
5. Ejecutar `make dev`.
6. Abrir `http://localhost:8000/health`.
7. Abrir `http://localhost:5173`.
8. Para detener, ejecutar `make stop`.

## Validaciones
- Lint: `make lint`
- Seguridad: `make scan`
- Tests: `make test`

## Resultado SCA (Actual)
- `npm audit --audit-level=high`: sin vulnerabilidades HIGH/CRITICAL.
- Hallazgos actuales: 5 vulnerabilidades MODERATE en cadena `vite/vitest/esbuild`
	orientadas al servidor de desarrollo.
- Mitigación pendiente: actualizar a versiones no vulnerables (requiere cambios
	potencialmente incompatibles en Vitest mayor).

## Contrato de Salud
- `GET /health` retorna `200` con `{ "status": "ok" }` cuando Atlas responde.
- `GET /health` retorna `503` con `{ "status": "error", "detail": "database unavailable" }` cuando Atlas no responde.
