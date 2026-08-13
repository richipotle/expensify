# Expense Payment Manager

Aplicación web empresarial para la gestión de gastos y pagos. Permite registrar gastos corporativos, gestionarlos a través de un flujo de aprobación, vincularlos con pagos desde cuentas bancarias y visualizar el estado financiero mediante un dashboard con gráficos.

Construida con Django + Django REST Framework (API) + Bootstrap 5 + Chart.js (frontend), con despliegue previsto en Render.com.

## Requisitos previos

- Python 3.11+ (o versión compatible con Django 5.0.6)
- pip
- Git (opcional, para clonar el repositorio)

## Cómo levantar el proyecto localmente

### 1. Crear y activar un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar el archivo de ejemplo y ajustar los valores:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Variables definidas en `.env`:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. Generar una nueva y aleatoria por entorno. |
| `DEBUG` | `True`/`False`. Usar `False` en producción. |
| `DJANGO_ENV` | `development` (usa SQLite) o `production` (usa PostgreSQL vía `DATABASE_URL`). |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL, usada solo cuando `DJANGO_ENV=production`. |
| `DJANGO_ADMIN_USERNAME` | Usuario del superusuario por defecto. |
| `DJANGO_ADMIN_EMAIL` | Email del superusuario por defecto. |
| `DJANGO_ADMIN_PASSWORD` | Contraseña del superusuario por defecto (requerida para crearlo). |

### 4. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear el usuario administrador por defecto

Este comando lee `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_EMAIL` y `DJANGO_ADMIN_PASSWORD` desde `.env` y crea el superusuario si aún no existe (es idempotente):

```bash
python manage.py create_default_admin
```

### 6. Cargar datos de ejemplo (opcional)

Crea usuarios, cuentas bancarias, gastos y pagos de demostración cubriendo los distintos estados del sistema. También es idempotente (identifica los datos con el prefijo `demo_`):

```bash
python manage.py seed_data
```

### 7. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación quedará disponible en `http://127.0.0.1:8000/`. El panel de administración de Django está en `http://127.0.0.1:8000/admin/`.

## Documentación de la API REST

Todos los endpoints de la API se encuentran bajo el prefijo `/api/` y son de **solo lectura**. **Requieren autenticación HTTP Basic** (usuario y contraseña de una cuenta válida del sistema) en todas las solicitudes.

Si una solicitud llega sin credenciales válidas, la API responde con **HTTP 401** y un mensaje de error en formato JSON.

### `GET /api/expenses/`

Lista todos los gastos (`Expense`) con todos sus campos.

**Autenticación:** HTTP Basic requerida.

**Parámetros de filtro (query params):**
- `estado`: filtra por coincidencia exacta con `BORRADOR`, `APROBADO`, `PAGADO` o `CANCELADO`.
- `fecha`: filtra por fecha exacta (formato `YYYY-MM-DD`).

Ejemplo: `GET /api/expenses/?estado=APROBADO&fecha=2024-02-05`

**Ejemplo de respuesta (200 OK):**

```json
[
    {
        "id": 4,
        "titulo": "Demo - Campaña de marketing digital",
        "descripcion": "Campaña publicitaria en redes sociales.",
        "monto_total": "6000.00",
        "categoria": "MARKETING",
        "fecha": "2024-02-05",
        "estado": "APROBADO",
        "creado_por": 1,
        "creado_en": "2024-02-05T10:00:00Z",
        "actualizado_en": "2024-02-05T10:00:00Z",
        "monto_pendiente": "6000.00"
    }
]
```

### `GET /api/expenses/{id}/`

Devuelve el detalle de un gasto específico, incluyendo el campo calculado `monto_pendiente` (monto total menos la suma de pagos en estado `EFECTUADO`).

**Autenticación:** HTTP Basic requerida.

**Ejemplo de respuesta (200 OK):**

```json
{
    "id": 4,
    "titulo": "Demo - Campaña de marketing digital",
    "descripcion": "Campaña publicitaria en redes sociales.",
    "monto_total": "6000.00",
    "categoria": "MARKETING",
    "fecha": "2024-02-05",
    "estado": "APROBADO",
    "creado_por": 1,
    "creado_en": "2024-02-05T10:00:00Z",
    "actualizado_en": "2024-02-05T10:00:00Z",
    "monto_pendiente": "6000.00"
}
```

### `GET /api/payments/`

Lista todos los pagos (`Payment`) con todos sus campos.

**Autenticación:** HTTP Basic requerida.

**Parámetros de filtro (query params):**
- `estado`: filtra por coincidencia exacta con `PENDIENTE`, `APROBADO`, `EFECTUADO` o `CANCELADO`.
- `fecha`: filtra por fecha exacta (formato `YYYY-MM-DD`).

Ejemplo: `GET /api/payments/?estado=EFECTUADO&fecha=2024-02-11`

**Ejemplo de respuesta (200 OK):**

```json
[
    {
        "id": 3,
        "gasto": 5,
        "cuenta_bancaria": 1,
        "monto": "10000.00",
        "fecha": "2024-02-11",
        "estado": "EFECTUADO",
        "referencia": "TRANSF-DEMO-003",
        "notas": "Pago de nómina efectuado.",
        "creado_por": 2,
        "creado_en": "2024-02-11T09:00:00Z",
        "actualizado_en": "2024-02-11T09:05:00Z"
    }
]
```

### `GET /api/payments/{id}/`

Devuelve el detalle de un pago específico con todos sus campos.

**Autenticación:** HTTP Basic requerida.

**Ejemplo de respuesta (200 OK):**

```json
{
    "id": 3,
    "gasto": 5,
    "cuenta_bancaria": 1,
    "monto": "10000.00",
    "fecha": "2024-02-11",
    "estado": "EFECTUADO",
    "referencia": "TRANSF-DEMO-003",
    "notas": "Pago de nómina efectuado.",
    "creado_por": 2,
    "creado_en": "2024-02-11T09:00:00Z",
    "actualizado_en": "2024-02-11T09:05:00Z"
}
```

### `GET /api/bank-accounts/`

Lista todas las cuentas bancarias (`BankAccount`) con todos sus campos. No soporta filtros por `estado`/`fecha` (la cuenta bancaria no tiene esos campos).

**Autenticación:** HTTP Basic requerida.

**Ejemplo de respuesta (200 OK):**

```json
[
    {
        "id": 1,
        "nombre": "Cuenta Demo Principal",
        "banco": "Banco Nacional",
        "numero_cuenta": "1001",
        "saldo_actual": "50000.00",
        "moneda": "USD",
        "activa": true,
        "creado_en": "2024-01-01T00:00:00Z",
        "actualizado_en": "2024-01-01T00:00:00Z"
    }
]
```

### `GET /api/bank-accounts/{id}/`

Devuelve el detalle de una cuenta bancaria específica con todos sus campos.

**Autenticación:** HTTP Basic requerida.

**Ejemplo de respuesta (200 OK):**

```json
{
    "id": 1,
    "nombre": "Cuenta Demo Principal",
    "banco": "Banco Nacional",
    "numero_cuenta": "1001",
    "saldo_actual": "50000.00",
    "moneda": "USD",
    "activa": true,
    "creado_en": "2024-01-01T00:00:00Z",
    "actualizado_en": "2024-01-01T00:00:00Z"
}
```

### `GET /api/dashboard/summary/`

Devuelve el resumen financiero agregado utilizado en el dashboard.

**Autenticación:** HTTP Basic requerida.

**Ejemplo de respuesta (200 OK):**

```json
{
    "total_gastos": "36350.00",
    "total_pagado": "18000.00",
    "total_pendiente": "18350.00",
    "saldo_total_activo": "85000.00"
}
```

### Errores de autenticación

Cualquier solicitud a un endpoint de la API sin credenciales HTTP Basic válidas recibe una respuesta:

**HTTP 401 Unauthorized**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Despliegue en Render

El proyecto incluye los archivos necesarios para desplegarse en [Render.com](https://render.com/) como un Web Service:

- **`Procfile`**: define el comando de release (migraciones + creación del admin por defecto) y el comando web (`gunicorn`).
- **`build.sh`**: script de build que instala dependencias y ejecuta `collectstatic`.
- **Whitenoise**: sirve los archivos estáticos directamente desde la aplicación, sin necesidad de un servidor/CDN adicional.
- **`dj-database-url`**: permite configurar la base de datos PostgreSQL de producción a partir de una única variable `DATABASE_URL`.

### Variables de entorno requeridas en Render

Configurar las siguientes variables de entorno en el panel del servicio de Render:

| Variable | Descripción |
|---|---|
| `DJANGO_ENV` | Debe ser `production` para activar la configuración de PostgreSQL, Whitenoise, etc. |
| `DATABASE_URL` | Cadena de conexión a la base de datos PostgreSQL (Render la provee automáticamente si se crea una base de datos administrada, o se puede pegar manualmente). |
| `SECRET_KEY` | Clave secreta de Django. Generar una nueva y aleatoria específica para producción. |
| `DEBUG` | Debe ser `False` en producción. |
| `DJANGO_ADMIN_USERNAME` | Usuario del superusuario por defecto, creado automáticamente en el paso de `release`. |
| `DJANGO_ADMIN_EMAIL` | Email del superusuario por defecto. |
| `DJANGO_ADMIN_PASSWORD` | Contraseña del superusuario por defecto. |

### Comandos de build y arranque

- **Build Command:** `./build.sh`
- **Release Command:** `python manage.py migrate && python manage.py create_default_admin` (definido en `Procfile`, Render lo ejecuta automáticamente en cada deploy).
- **Start Command:** `gunicorn config.wsgi --log-file -` (definido en `Procfile`).
