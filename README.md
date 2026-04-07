# NexusERP

Un sistema de planificación de recursos empresariales (ERP) moderno y escalable, diseñado para gestionar operaciones comerciales integrales incluyendo inventario, ventas, compras, clientes y más.

## 📋 Descripción

NexusERP es una aplicación full-stack que proporciona una solución completa para la gestión empresarial. Combina una API backend robusta basada en FastAPI con un frontend interactivo moderno, complementado con autenticación segura y una base de datos MongoDB escalable.

### Características Principales

- **Autenticación y Autorización**: Sistema JWT con roles de usuario
- **Gestión de Catálogo**: Administración de productos y categorías
- **Gestión de Inventario**: Control de stock en tiempo real
- **CRM de Clientes**: Gestión integral de clientes
- **Gestión de Compras**: Procesos de compra y proveedores
- **Punto de Venta (POS)**: Sistema de facturación e invoicing
- **Auditoría y Logs**: Registros de operaciones para compliance

## 🏗️ Estructura del Proyecto

```
nexuserp/
├── apps/
│   ├── backend/          # API FastAPI (Python)
│   │   ├── auth/         # Autenticación y autorización
│   │   ├── catalog/      # Gestión de productos
│   │   ├── inventory/    # Gestión de inventario
│   │   ├── customers/    # CRM de clientes
│   │   ├── purchases/    # Gestión de compras
│   │   ├── sales/        # Gestión de ventas
│   │   ├── core/         # Configuración central
│   │   ├── tests/        # Suite de pruebas
│   │   └── main.py       # Punto de entrada
│   └── frontend/         # Aplicación Vite + TypeScript
│       └── src/          # Código fuente frontend
├── docker-compose.yml    # Orquestación de servicios
├── Makefile             # Comandos de desarrollo
└── README.md            # Este archivo
```

## 🔧 Requisitos Previos

- **Docker** y **Docker Compose** (recomendado para desarrollo)
- **Python 3.11+** (para desarrollo local del backend)
- **Node.js 18+** (para desarrollo local del frontend)
- **MongoDB 4.4+** (si ejecutas sin Docker)

## ⚙️ Instalación

### Con Docker (Recomendado)

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd nexuserp
   ```

2. **Configurar variables de entorno**
   ```bash
   # Backend
   cp apps/backend/.env.example apps/backend/.env
   # Editá el archivo .env con tus valores
   
   # Frontend
   cp apps/frontend/.env.example apps/frontend/.env
   ```

3. **Inicia los servicios**
   ```bash
   make dev
   ```

   Esto iniciará:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173
   - MongoDB: localhost:27017

### Instalación Local

#### Backend

1. **Crear entorno virtual**
   ```bash
   cd apps/backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # o
   source .venv/bin/activate  # Linux/macOS
   ```

2. **Instalar dependencias**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Edita .env según sea necesario
   ```

4. **Ejecutar el servidor**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend

1. **Instalar dependencias**
   ```bash
   cd apps/frontend
   npm install
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Asegúrate de que apunte al backend correcto
   ```

3. **Ejecutar servidor de desarrollo**
   ```bash
   npm run dev
   ```

## 📚 Uso

### Comandos Disponibles

```bash
# Desarrollo (con Docker)
make dev              # Inicia todos los servicios

# Control
make stop             # Detiene los servicios

# Linting y Formato
make lint             # Ejecuta linters (ruff, mypy, eslint)

# Testing
make test             # Ejecuta todas las pruebas
                      # - Pytest para backend
                      # - Vitest para frontend

# Seguridad
make scan             # Escanea vulnerabilidades
                      # - Bandit para Python
                      # - detect-secrets
                      # - npm audit para JavaScript
```

## 🔐 Seguridad

El proyecto incluye múltiples capas de seguridad:

- **Autenticación JWT**: Tokens seguros con expiración configurable
- **Hash de Contraseñas**: Bcrypt para almacenamiento seguro
- **Escaneado de Vulnerabilidades**: Bandit, detect-secrets, npm audit
- **Type Safety**: MyPy strict mode para Python
- **Validación de Entrada**: Pydantic v2 con validación rigurosa

## 📦 Stack Tecnológico

### Backend
- **FastAPI**: Framework web asincrónico moderno
- **Uvicorn**: Servidor ASIR de alto rendimiento
- **Motor**: Driver async para MongoDB
- **Pydantic v2**: Validación de datos y serialización
- **PyJWT**: Autenticación basada en tokens
- **Bcrypt**: Hashing seguro de contraseñas

### Frontend
- **Vite**: Build tool ultrarrápido
- **TypeScript**: Tipado estático
- **Modern CSS**: Estilos contemporáneos

### Base de Datos
- **MongoDB**: Base de datos NoSQL escalable

### Desarrollo
- **Pytest**: Testing framework para Python
- **Ruff**: Linter ultra-rápido
- **MyPy**: Verificación de tipos
- **ESLint**: Linting para JavaScript/TypeScript
- **Vitest**: Testing para frontend

## 🧪 Testing

### Ejecutar Pruebas del Backend

```bash
# Con Docker
make test

# Desarrollo local
cd apps/backend
pytest                    # Todas las pruebas
pytest tests/test_auth.py # Archivo específico
pytest -v --cov          # Con cobertura
```

### Ejecutar Pruebas del Frontend

```bash
# Con Docker
make test

# Desarrollo local
cd apps/frontend
npm run test              # Todas las pruebas
npm run test:ui           # Con interfaz gráfica
```

## 📊 Estructura de Módulos del Backend

Cada módulo funcional sigue una arquitectura en capas:

```
modulo/
├── __init__.py
├── dependencies.py    # Inyección de dependencias
├── schemas.py        # Modelos Pydantic
├── repositories/     # Acceso a datos
├── routers/          # Endpoints HTTP
├── services/         # Lógica de negocio
└── utils/            # Utilidades específicas
```

### Módulos Disponibles

- **auth**: Autenticación, autorización y gestión de usuarios
- **catalog**: Productos y categorías
- **inventory**: Control de inventario
- **customers**: Gestión de relaciones con clientes
- **purchases**: Procesos de compra y proveedores
- **sales**: Gestión de ventas
- **core**: Configuración global, database, esquemas comunes

## 🚀 Deployment

### Variables de Entorno Importantes

```env
# Backend
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=nexuserp
JWT_SECRET=tu-secreto-super-seguro
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Frontend
VITE_API_URL=http://localhost:8000
```

### Production

Para desplegar en producción:

1. Configura todas las variables de entorno de forma segura
2. Usa certificados SSL/TLS
3. Configura una base de datos MongoDB gestionada (Atlas, etc.)
4. Implementa rate limiting y CORS apropiadamente
5. Usa un reverse proxy (Nginx, Traefik)
6. Configura logging y monitoring

## 📖 Documentación API

Una vez que el backend esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Linting y Calidad de Código

### Backend

```bash
# Verificar con ruff
ruff check .

# Verificar tipos con mypy
mypy .

# Formateo automático de código
ruff format .
```

### Frontend

```bash
# Lint
npm run lint

# Formateo
npm run format
```

## 🔧 Health Check

El backend proporciona un endpoint de salud para verificar la disponibilidad:

- **Request**: `GET /health`
- **Success**: `HTTP 200 { "status": "ok" }` (MongoDB disponible)
- **Error**: `HTTP 503 { "status": "error", "detail": "database unavailable" }` (MongoDB no disponible)

## 🐛 Troubleshooting

### "Missing .env file"
Asegúrate de crear los archivos `.env` a partir de los templates `.env.example`.

### MongoDB Connection Error
Verifica que MongoDB esté corriendo y que `MONGODB_URL` sea correcto en el archivo `.env`.

### Puerto ya en uso
Si el puerto 8000 o 5173 está en uso, cambia la configuración en `docker-compose.yml` o ejecuta en puertos diferentes.

### Problemas de Permisos en Windows
Si tienes problemas con permisos en PowerShell, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 Convenciones de Código

- **Python**: Seguir PEP 8, configurado en `ruff`
- **TypeScript**: ESLint + Prettier
- **Commit Messages**: Preferentemente en presente imperativo
- **Branch Naming**: `feature/`, `bugfix/`, `hotfix/`

## 📄 Licencia

Este proyecto está disponible bajo licencia a ser definida.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para reportar issues o hacer preguntas, utiliza la sección de Issues del repositorio.

---

**Última actualización**: Abril de 2026
