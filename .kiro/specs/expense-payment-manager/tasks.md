# Plan de Implementación: Expense Payment Manager

## Overview

Este plan convierte el diseño en pasos de código incrementales, pensados para un desarrollador junior/graduate sin experiencia previa con Django. Cada tarea indica el archivo concreto a crear/modificar y se apoya en la anterior: primero se monta el proyecto base, luego los modelos, luego la lógica de negocio en `services.py`, después las vistas/formularios, las plantillas, el dashboard, la API REST, el admin, los datos de demo, y por último la preparación (no ejecución) del despliegue. Las tareas de test (marcadas con `*`) son opcionales de ejecutar pero se recomienda no saltarlas porque validan las 29 properties del diseño.

> Nota para el desarrollador junior: cada bloque de "Capa de servicios" es el corazón del sistema — ahí vive toda regla de negocio (quién puede aprobar, cuándo se descuenta saldo, etc.). Las vistas solo deben llamar a estas funciones y mostrar mensajes de éxito/error.

## Tasks

- [x] 1. Configurar el entorno de desarrollo y la base del proyecto Django
  - [x] 1.1 Crear el entorno virtual e instalar Django
    - Crear un entorno virtual con `python -m venv venv` y activarlo
    - Instalar Django con `pip install Django==5.0.6`
    - Verificar la instalación con `python -m django --version`
    - _Requirements: 10.6_
  - [x] 1.2 Crear el proyecto Django (`config`) y las apps del dominio
    - Ejecutar `django-admin startproject config .` en la raíz del repo
    - Ejecutar `python manage.py startapp accounts`, `startapp expenses`, `startapp payments`, `startapp dashboard`, `startapp api`
    - Crear la carpeta `templates/` en la raíz con subcarpeta `registration/`
    - Crear dentro de cada app la carpeta `templates/<app>/` y (donde aplique) `tests/` con un `__init__.py`
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  - [x] 1.3 Configurar `config/settings.py` con variables de entorno
    - Instalar `python-decouple` (`pip install python-decouple==3.8`) y usar `config('SECRET_KEY')`, `config('DEBUG', cast=bool, default=False)`, `config('DJANGO_ENV', default='development')`
    - Registrar las apps `accounts`, `expenses`, `payments`, `dashboard`, `api` en `INSTALLED_APPS`
    - Configurar `TEMPLATES` para que busque en la carpeta `templates/` de la raíz además de las de cada app
    - Configurar `DATABASES`: SQLite si `DJANGO_ENV != 'production'`, dejar un bloque comentado para PostgreSQL que se completará en la tarea de despliegue
    - Configurar `LOGIN_URL = 'login'` y `LOGIN_REDIRECT_URL = 'dashboard:home'`
    - _Requirements: 10.7, 10.8, 1.5_
  - [x] 1.4 Crear `requirements.txt` con versiones pinneadas
    - Incluir `Django==5.0.6`, `djangorestframework==3.15.2`, `django-filter==24.2`, `python-decouple==3.8`, `psycopg2-binary==2.9.9`, `gunicorn==22.0.0`, `whitenoise==6.6.0`, `dj-database-url==2.2.0`, `hypothesis==6.103.1`, `pytest==8.2.2`, `pytest-django==4.8.0`
    - _Requirements: 10.6_
  - [x] 1.5 Crear plantilla de variables de entorno `.env.example`
    - Definir `SECRET_KEY`, `DEBUG`, `DJANGO_ENV`, `DATABASE_URL`, `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_EMAIL`, `DJANGO_ADMIN_PASSWORD` con valores de ejemplo (nunca reales)
    - Copiar `.env.example` a `.env` localmente (este archivo NO se versiona, agregarlo a `.gitignore`)
    - _Requirements: 1.5, 10.8_

- [x] 2. Implementar los modelos de datos y migraciones
  - [x] 2.1 Implementar `accounts/models.py` (`BankAccount`)
    - Campos: `nombre`, `banco`, `numero_cuenta` (con `RegexValidator` de 4 dígitos), `saldo_actual` (`DecimalField`, `MinValueValidator(0)`), `moneda` (`TextChoices`), `activa`, timestamps
    - Implementar `clean()` para rechazar `saldo_actual` negativo y `__str__`
    - _Requirements: 7.6_
  - [x] 2.2 Implementar `expenses/models.py` (`Expense`)
    - Campos: `titulo`, `descripcion`, `monto_total` (`MinValueValidator(0.01)`), `categoria` (`TextChoices`), `fecha`, `estado` (`TextChoices`, default `BORRADOR`), `creado_por` (FK a `settings.AUTH_USER_MODEL`), timestamps
    - Implementar la `property` `monto_pendiente` (monto_total menos suma de pagos EFECTUADO)
    - Implementar `clean()` para impedir que un gasto CANCELADO cambie de estado
    - _Requirements: 2.8, 2.1, 2.3, 3.7_
  - [x] 2.3 Implementar `payments/models.py` (`Payment`)
    - Campos: `gasto` (FK a `expenses.Expense`), `cuenta_bancaria` (FK a `accounts.BankAccount`), `monto` (`MinValueValidator(0.01)`), `fecha`, `estado` (`TextChoices`, default `PENDIENTE`), `referencia`, `notas`, `creado_por`, timestamps
    - Implementar `clean()` para rechazar `monto <= 0`
    - _Requirements: 4.10, 4.1_
  - [x] 2.4 Generar y aplicar las migraciones iniciales
    - Ejecutar `python manage.py makemigrations accounts expenses payments`
    - Ejecutar `python manage.py migrate`
    - Verificar en `python manage.py shell` que las tres tablas existen
    - _Requirements: 10.7_
  - [ ]* 2.5 Escribir unit tests de validación de modelo
    - En `accounts/tests/test_models.py`, `expenses/tests/test_models.py`, `payments/tests/test_models.py`: casos de éxito y de rechazo de `clean()` (saldo negativo, monto <= 0)
    - _Requirements: 7.6, 4.10_
  - [ ]* 2.6 Property test: Property 1 (gasto nuevo inicia en BORRADOR)
    - En `expenses/tests/test_models.py`, usar Hypothesis para generar título/monto/categoría/fecha válidos y comprobar que `Expense.objects.create(...)` siempre resulta en `estado == BORRADOR`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 1: Un gasto recién creado siempre inicia en BORRADOR`
    - **Validates: Requirements 2.1**
  - [ ]* 2.7 Property test: Property 2 (monto pendiente = monto total - pagos efectuados)
    - En `expenses/tests/test_models.py`, generar un gasto y una lista de pagos con estados y montos arbitrarios, comprobar que `expense.monto_pendiente` es exactamente `monto_total` menos la suma de montos de pagos EFECTUADO (y que pagos en otros estados no se cuentan)
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 2: El monto pendiente es el monto total menos los pagos efectuados`
    - **Validates: Requirements 2.3**

- [x] 3. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implementar la capa de servicios: `accounts`
  - [x] 4.1 Implementar `accounts/services.py`: `desactivar_cuenta(cuenta)`
    - Verificar que no existan `Payment` en estado `PENDIENTE` o `APROBADO` asociados a la cuenta antes de poner `activa = False`
    - Lanzar `ValidationError` con el número exacto de pagos activos encontrados si la validación falla
    - _Requirements: 7.4, 7.5_
  - [ ]* 4.2 Property test: Property 21 (desactivación solo sin pagos activos)
    - En `accounts/tests/test_services.py`, generar una cuenta con una cantidad arbitraria de pagos en estados arbitrarios y comprobar que `desactivar_cuenta` tiene éxito si y solo si no hay pagos PENDIENTE/APROBADO, y que el mensaje de error reporta el número exacto cuando falla
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 21: Una cuenta solo se desactiva si no tiene pagos activos`
    - **Validates: Requirements 7.4, 7.5**
  - [ ]* 4.3 Escribir unit tests de ejemplo para `desactivar_cuenta`
    - Casos concretos: cuenta sin pagos, cuenta con un pago EFECTUADO (debe permitir desactivar), cuenta con un pago PENDIENTE (debe rechazar)
    - _Requirements: 7.4, 7.5_

- [x] 5. Implementar la capa de servicios: `expenses`
  - [x] 5.1 Implementar `expenses/services.py`: `aprobar_gasto(gasto, user)` y `cancelar_gasto(gasto, user)`
    - `aprobar_gasto`: solo transiciona BORRADOR → APROBADO, en cualquier otro caso lanza `ValidationError`
    - `cancelar_gasto`: solo transiciona BORRADOR/APROBADO → CANCELADO, en cualquier otro caso lanza `ValidationError`
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6, 3.7_
  - [x] 5.2 Implementar `expenses/services.py`: `recalcular_estado_pago(gasto)`
    - Si `gasto.estado == CANCELADO`, no hace nada (estado terminal)
    - Si `monto_pendiente <= 0`, transiciona a PAGADO; si `monto_pendiente > 0` y el estado era PAGADO, vuelve a APROBADO
    - _Requirements: 3.8, 5.9_
  - [ ]* 5.3 Property test: Property 5 (aprobar solo desde BORRADOR)
    - En `expenses/tests/test_services.py`, generar un gasto en un estado arbitrario y comprobar que `aprobar_gasto` cambia a APROBADO si y solo si el estado inicial era BORRADOR
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 5: Aprobar un gasto solo tiene éxito desde BORRADOR`
    - **Validates: Requirements 3.1, 3.2, 3.3**
  - [ ]* 5.4 Property test: Property 6 (cancelar solo desde BORRADOR o APROBADO)
    - Generar un gasto en un estado arbitrario y comprobar que `cancelar_gasto` cambia a CANCELADO si y solo si el estado inicial era BORRADOR o APROBADO
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 6: Cancelar un gasto solo tiene éxito desde BORRADOR o APROBADO`
    - **Validates: Requirements 3.5, 3.6**
  - [ ]* 5.5 Property test: Property 7 (CANCELADO es terminal)
    - Generar un gasto CANCELADO y aplicar `aprobar_gasto`, `cancelar_gasto` y `recalcular_estado_pago`; comprobar que el estado permanece CANCELADO en los tres casos
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 7: Un gasto CANCELADO es un estado terminal`
    - **Validates: Requirements 3.7**
  - [ ]* 5.6 Property test: Property 8 (suma de pagos efectuados dispara PAGADO)
    - Generar un gasto APROBADO y una secuencia arbitraria de pagos EFECTUADO cuya suma varía; llamar `recalcular_estado_pago` tras cada pago y comprobar que el estado cambia a PAGADO exactamente cuando la suma alcanza o supera `monto_total`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 8: La suma de pagos efectuados dispara el estado PAGADO`
    - **Validates: Requirements 3.8**

- [x] 6. Implementar la capa de servicios: `payments`
  - [x] 6.1 Implementar `payments/services.py`: `crear_pago(gasto, cuenta, monto, fecha, referencia, notas, user)`
    - Validar en orden: gasto en estado APROBADO, `monto <= gasto.monto_pendiente`, `monto <= cuenta.saldo_actual`, no duplicado (mismo gasto + cuenta + monto + fecha)
    - Crear el `Payment` en estado PENDIENTE solo si todas las validaciones pasan
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ]* 6.2 Property test: Property 9 (pago nuevo inicia en PENDIENTE)
    - En `payments/tests/test_services.py`, generar datos válidos de pago y comprobar que `crear_pago` siempre resulta en `estado == PENDIENTE`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 9: Un pago recién creado siempre inicia en PENDIENTE`
    - **Validates: Requirements 4.1**
  - [ ]* 6.3 Property test: Property 10 (requiere gasto APROBADO)
    - Generar un gasto en estado arbitrario y comprobar que `crear_pago` solo tiene éxito si el estado es APROBADO, y que no se crea ningún `Payment` cuando falla
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 10: Crear un pago requiere que el gasto esté APROBADO`
    - **Validates: Requirements 4.2**
  - [ ]* 6.4 Property test: Property 11 (monto ≤ monto pendiente)
    - Generar un gasto APROBADO con `monto_pendiente` conocido y un monto propuesto arbitrario; comprobar que `crear_pago` rechaza si excede el pendiente y permite si es menor o igual
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 11: El monto de un pago no puede exceder el monto pendiente del gasto`
    - **Validates: Requirements 4.3**
  - [ ]* 6.5 Property test: Property 12 (monto ≤ saldo de la cuenta)
    - Generar una cuenta con saldo conocido y un monto propuesto arbitrario; comprobar que `crear_pago` rechaza si excede el saldo y permite si es menor o igual (con las demás condiciones satisfechas)
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 12: El monto de un pago no puede exceder el saldo de la cuenta`
    - **Validates: Requirements 4.4**
  - [ ]* 6.6 Property test: Property 13 (no se permiten pagos duplicados)
    - Generar los mismos datos (gasto, cuenta, monto, fecha) y llamar `crear_pago` dos veces; comprobar que la primera llamada tiene éxito y la segunda lanza `ValidationError`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 13: No se permiten pagos duplicados`
    - **Validates: Requirements 4.5**
  - [x] 6.7 Implementar `payments/services.py`: `aprobar_pago(payment)`
    - Solo transiciona PENDIENTE → APROBADO, en cualquier otro caso lanza `ValidationError`
    - _Requirements: 5.1, 5.2_
  - [ ]* 6.8 Property test: Property 15 (aprobar solo desde PENDIENTE)
    - Generar un pago en un estado arbitrario y comprobar que `aprobar_pago` cambia a APROBADO si y solo si el estado inicial era PENDIENTE
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 15: Aprobar un pago solo tiene éxito desde PENDIENTE`
    - **Validates: Requirements 5.1, 5.2**
  - [x] 6.9 Implementar `payments/services.py`: `efectuar_pago(payment)`
    - Usar `transaction.atomic()`: validar `cuenta.saldo_actual >= payment.monto`, descontar el saldo, transicionar a EFECTUADO y llamar `expenses.services.recalcular_estado_pago(payment.gasto)`
    - Lanzar `ValidationError` con el saldo disponible si es insuficiente, sin modificar nada
    - _Requirements: 5.3, 5.4, 5.5_
  - [ ]* 6.10 Property test: Property 16 (efectuar es consistente con el saldo)
    - Generar un pago APROBADO y un saldo de cuenta arbitrario; comprobar que `efectuar_pago` tiene éxito y descuenta exactamente `monto` si y solo si `saldo_actual >= monto`, y que rechaza sin cambios en caso contrario
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 16: Efectuar un pago es consistente con el saldo de la cuenta`
    - **Validates: Requirements 5.3, 5.4, 5.5**
  - [x] 6.11 Implementar `payments/services.py`: `cancelar_pago(payment)`
    - Usar `transaction.atomic()`: si el pago estaba EFECTUADO, restaurar `saldo_actual += monto` y llamar `recalcular_estado_pago`; si estaba PENDIENTE/APROBADO, solo transicionar a CANCELADO sin tocar saldos
    - _Requirements: 5.6, 5.7, 5.8, 5.9_
  - [ ]* 6.12 Property test: Property 17 (cancelar revierte saldo solo si estaba EFECTUADO)
    - Generar un pago en estado EFECTUADO, PENDIENTE o APROBADO y comprobar el comportamiento de `cancelar_pago` sobre el saldo de la cuenta según el estado inicial
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 17: Cancelar un pago revierte el saldo solo si estaba EFECTUADO`
    - **Validates: Requirements 5.7, 5.8**
  - [ ]* 6.13 Property test: Property 18 (cancelar un pago efectuado reevalúa el gasto)
    - Generar un gasto PAGADO con un pago EFECTUADO asociado y cancelar dicho pago; comprobar que si el `monto_pendiente` resultante es mayor a cero, el gasto vuelve a APROBADO
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 18: Cancelar un pago efectuado reevalúa el estado del gasto`
    - **Validates: Requirements 5.9**

- [x] 7. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implementar vistas y formularios: `accounts`
  - [x] 8.1 Implementar `accounts/forms.py`: `BankAccountForm`
    - `ModelForm` sobre `BankAccount`; excluir `saldo_actual` del formulario de edición (solo se permite en creación, con valor inicial) para que nunca se modifique vía formulario
    - _Requirements: 7.3, 7.6_
  - [x] 8.2 Implementar las vistas de `accounts/views.py`
    - `BankAccountListView`, `BankAccountDetailView`, `BankAccountCreateView`, `BankAccountUpdateView` (CBVs con `LoginRequiredMixin`)
    - FBV `bankaccount_deactivate(request, pk)` que llama a `services.desactivar_cuenta` dentro de un `try/except ValidationError`, mostrando `messages.error`/`messages.success`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 1.1_
  - [x] 8.3 Configurar `accounts/urls.py` con los nombres de ruta `list`, `create`, `detail`, `update`, `deactivate`
    - _Requirements: 10.3_
  - [ ]* 8.4 Property test: Property 20 (editar cuenta nunca modifica el saldo)
    - En `accounts/tests/test_views.py`, usar el cliente de pruebas de Django para enviar un `POST` de edición con un `saldo_actual` distinto y comprobar que el valor en base de datos no cambia
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 20: Editar una cuenta bancaria nunca modifica el saldo`
    - **Validates: Requirements 7.3**
  - [ ]* 8.5 Escribir unit tests de vistas de `accounts`
    - Comprobar status codes, redirecciones tras crear/editar y el mensaje de error al desactivar una cuenta con pagos activos
    - _Requirements: 7.1, 7.2, 7.4_

- [x] 9. Implementar vistas y formularios: `expenses`
  - [x] 9.1 Implementar `expenses/forms.py`: `ExpenseForm`
    - `ModelForm` sobre `Expense` con los campos editables (título, descripción, monto_total, categoría, fecha); `creado_por` se asigna en la vista, no en el formulario
    - _Requirements: 2.8_
  - [x] 9.2 Implementar CBVs de `expenses/views.py` con restricción de edición/eliminación
    - `ExpenseListView`, `ExpenseDetailView` (incluye `monto_pendiente` e historial de pagos en el contexto), `ExpenseCreateView` (asigna `creado_por = request.user`)
    - `ExpenseUpdateView` y `ExpenseDeleteView`: en `dispatch()` o `get_queryset()`, verificar `estado == BORRADOR`; si no, redirigir con `messages.error` sin permitir la operación
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [ ]* 9.3 Property test: Property 3 (solo BORRADOR es editable)
    - En `expenses/tests/test_views.py`, generar un gasto en estado arbitrario e intentar editarlo vía `POST`; comprobar que tiene éxito si y solo si el estado era BORRADOR
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 3: Solo los gastos en BORRADOR son editables`
    - **Validates: Requirements 2.4, 2.5**
  - [ ]* 9.4 Property test: Property 4 (solo BORRADOR es eliminable)
    - Generar un gasto en estado arbitrario e intentar eliminarlo vía `POST`; comprobar que tiene éxito (el registro desaparece) si y solo si el estado era BORRADOR
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 4: Solo los gastos en BORRADOR son eliminables`
    - **Validates: Requirements 2.6, 2.7**
  - [x] 9.5 Implementar las FBVs de transición en `expenses/views.py`
    - `expense_approve(request, pk)` y `expense_cancel(request, pk)`: llaman a `services.aprobar_gasto`/`cancelar_gasto` dentro de `try/except ValidationError`, muestran diálogo de confirmación en el template antes del `POST`
    - `expense_generate_payment(request, pk)`: `GET` que redirige a `payments:create?expense_id=<pk>` solo si el gasto está APROBADO
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 6.1, 6.2, 6.4_
  - [x] 9.6 Configurar `expenses/urls.py` con todas las rutas del diseño (`list`, `create`, `detail`, `update`, `delete`, `approve`, `cancel`, `generate_payment`)
    - _Requirements: 10.1_
  - [ ]* 9.7 Escribir unit tests de vistas de `expenses`
    - Comprobar que el botón "Generar Pago" solo aparece cuando el gasto está APROBADO (verificar contexto/HTML) y los mensajes de error de las transiciones inválidas
    - _Requirements: 6.4, 3.3, 3.6_

- [x] 10. Implementar vistas y formularios: `payments`
  - [x] 10.1 Implementar `payments/forms.py`: `PaymentForm`
    - `ModelForm` sobre `Payment` con los campos `gasto`, `cuenta_bancaria`, `monto`, `fecha`, `referencia`, `notas`
    - _Requirements: 4.10_
  - [x] 10.2 Implementar CBVs de `payments/views.py`, incluyendo pre-llenado desde un gasto
    - `PaymentListView`, `PaymentDetailView`, `PaymentCreateView` (lee `?expense_id=` de query params, pre-llena `gasto` y sugiere `monto = gasto.monto_pendiente`; en `form_valid` llama a `services.crear_pago` capturando `ValidationError`)
    - _Requirements: 4.1, 4.6, 4.7, 6.2, 6.3_
  - [ ]* 10.3 Property test: Property 19 (monto sugerido = monto pendiente)
    - En `payments/tests/test_views.py`, generar un gasto APROBADO con historial de pagos arbitrario y comprobar que el valor inicial del campo `monto` en el formulario pre-llenado coincide exactamente con `monto_pendiente`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 19: El monto sugerido al generar un pago es el monto pendiente`
    - **Validates: Requirements 6.3**
  - [x] 10.4 Implementar `PaymentUpdateView` y `PaymentDeleteView` con restricción de edición
    - Verificar `estado == PENDIENTE` antes de permitir editar/eliminar, igual que en `expenses`
    - _Requirements: 4.8, 4.9_
  - [ ]* 10.5 Property test: Property 14 (solo PENDIENTE es editable)
    - Generar un pago en estado arbitrario e intentar editarlo vía `POST`; comprobar que tiene éxito si y solo si el estado era PENDIENTE
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 14: Solo los pagos en PENDIENTE son editables`
    - **Validates: Requirements 4.8, 4.9**
  - [x] 10.6 Implementar las FBVs de transición en `payments/views.py`
    - `payment_approve`, `payment_execute`, `payment_cancel`: llaman a los servicios correspondientes dentro de `try/except ValidationError`, con diálogo de confirmación para cancelar
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  - [x] 10.7 Configurar `payments/urls.py` con todas las rutas del diseño
    - _Requirements: 10.2_
  - [ ]* 10.8 Escribir unit tests de vistas de `payments`
    - Comprobar mensajes de error de `crear_pago` (gasto no aprobado, monto excede pendiente/saldo, duplicado) al enviarlos vía `POST` al `CreateView`
    - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [x] 11. Configurar autenticación y usuario administrador por defecto
  - [x] 11.1 Registrar login/logout y proteger vistas
    - En `config/urls.py`: `path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login")` y `LogoutView`
    - Confirmar que todas las CBVs usan `LoginRequiredMixin` y las FBVs usan `@login_required`
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [x] 11.2 Crear comando de gestión para el usuario administrador por defecto
    - Crear `accounts/management/commands/create_default_admin.py` que lea `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_EMAIL`, `DJANGO_ADMIN_PASSWORD` de las variables de entorno y cree un superusuario si no existe
    - _Requirements: 1.5_
  - [ ]* 11.3 Escribir unit tests de autenticación
    - Casos: acceso sin login redirige a `/accounts/login/`, login con credenciales válidas redirige al dashboard, login con credenciales inválidas muestra error, logout cierra sesión
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 12. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Crear templates base, navegación y login
  - [x] 13.1 Crear `templates/partials/navbar.html`
    - Barra de navegación Bootstrap 5 con enlaces a Dashboard, Gastos, Pagos, Cuentas y botón de Logout (visible solo si el usuario está autenticado)
    - _Requirements: 10.5_
  - [x] 13.2 Crear `templates/base.html`
    - Incluir Bootstrap 5 (CDN), bloque `{% block content %}`, bloque `{% block scripts %}`, `{% include 'partials/navbar.html' %}` y el contenedor para `django.contrib.messages`
    - _Requirements: 10.5_
  - [x] 13.3 Crear `templates/registration/login.html`
    - Extiende `base.html`; formulario de login con Bootstrap y bloque para mostrar errores de credenciales inválidas
    - _Requirements: 1.3_

- [x] 14. Crear templates de `accounts`, `expenses` y `payments`
  - [x] 14.1 Crear templates de `accounts` (`bankaccount_list.html`, `bankaccount_detail.html`, `bankaccount_form.html`)
    - Lista con nombre, banco, últimos 4 dígitos, saldo, moneda y badge de estado activa/inactiva (verde/gris)
    - _Requirements: 7.2_
  - [x] 14.2 Crear templates de `expenses` (`expense_list.html`, `expense_detail.html`, `expense_form.html`)
    - Lista con título, monto, categoría, fecha y badge de color por estado (BORRADOR=gris, APROBADO=azul, PAGADO=verde, CANCELADO=rojo)
    - Detalle: todos los campos, historial de pagos, monto pendiente, botones "Aprobar"/"Cancelar"/"Generar Pago" visibles solo según el estado, con modal de confirmación Bootstrap para cancelar
    - _Requirements: 2.2, 2.3, 3.4, 6.1, 6.4_
  - [x] 14.3 Crear templates de `payments` (`payment_list.html`, `payment_detail.html`, `payment_form.html`)
    - Lista con referencia, gasto, cuenta, monto, fecha y badge de color por estado
    - Detalle: todos los campos y el detalle del gasto asociado, botones "Aprobar"/"Efectuar"/"Cancelar" según estado, con modal de confirmación para cancelar
    - _Requirements: 4.6, 4.7, 5.6_

- [ ] 15. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Implementar el dashboard con agregaciones y Chart.js
  - [x] 16.1 Implementar `dashboard/services.py`: `get_summary()`
    - Devuelve `{total_gastos, total_pagado, total_pendiente, saldo_total_activo}` usando `aggregate(Sum(...))`
    - _Requirements: 8.1_
  - [ ]* 16.2 Property test: Property 22 (agregaciones exactas del resumen)
    - En `dashboard/tests/test_services.py`, generar conjuntos arbitrarios de gastos, pagos y cuentas y comprobar cada campo de `get_summary()` contra el cálculo manual esperado
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 22: Las tarjetas de resumen del dashboard son agregaciones exactas`
    - **Validates: Requirements 8.1, 9.7**
  - [x] 16.3 Implementar `dashboard/services.py`: `get_top_n(queryset, n=10)`
    - _Requirements: 8.2, 8.3_
  - [ ]* 16.4 Property test: Property 23 (top-N limitado y ordenado)
    - Generar una colección arbitraria de gastos/pagos y comprobar que `get_top_n` devuelve como máximo `n` elementos ordenados por fecha descendente
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 23: Las listas "últimos N" están limitadas y ordenadas`
    - **Validates: Requirements 8.2, 8.3**
  - [x] 16.5 Implementar `dashboard/services.py`: `get_expenses_by_status()` y `get_expenses_by_category()`
    - _Requirements: 8.4, 8.5_
  - [ ]* 16.6 Property test: Property 24 (agregaciones de gráficos suman al total)
    - Generar un conjunto arbitrario de gastos y comprobar que la suma de `get_expenses_by_status()` es igual al total de gastos, y que la suma de `get_expenses_by_category()` es igual a la suma de `monto_total`
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 24: Los datos de agregación de gráficos suman al total`
    - **Validates: Requirements 8.4, 8.5**
  - [x] 16.7 Implementar `dashboard/services.py`: `get_payments_by_month(months=6)`
    - _Requirements: 8.6_
  - [ ]* 16.8 Property test: Property 25 (pagos mensuales no exceden el total efectuado)
    - Generar un conjunto arbitrario de pagos con fechas variadas y comprobar que la suma de `get_payments_by_month(6)` es menor o igual a la suma total de pagos EFECTUADO
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 25: Los pagos mensuales agregados no exceden el total efectuado`
    - **Validates: Requirements 8.6**
  - [x] 16.9 Implementar `dashboard/views.py` (`DashboardHomeView`) y `dashboard/templates/dashboard/home.html`
    - Ensamblar las cuatro tarjetas, las dos tablas "últimos 10" y los tres gráficos Chart.js (dona por estado, barras por categoría, línea por mes) usando los datos anteriores serializados a JSON en el contexto
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  - [ ] 16.10 Configurar `dashboard/urls.py` y enlazarlo en `config/urls.py`
    - _Requirements: 10.1_

- [ ] 17. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Implementar la API REST con Django REST Framework
  - [x] 18.1 Instalar y configurar DRF y django-filter en `config/settings.py`
    - Agregar `rest_framework` y `django_filters` a `INSTALLED_APPS`
    - Configurar `REST_FRAMEWORK` con `DEFAULT_AUTHENTICATION_CLASSES = ['rest_framework.authentication.BasicAuthentication']` y `DEFAULT_PERMISSION_CLASSES = ['rest_framework.permissions.IsAuthenticated']`
    - _Requirements: 9.1, 10.4_
  - [x] 18.2 Implementar `api/serializers.py` y `api/filters.py`
    - `BankAccountSerializer`, `PaymentSerializer` (todos los campos del modelo)
    - `ExpenseSerializer` con campo adicional `monto_pendiente` vía `ReadOnlyField(source='monto_pendiente')`
    - `ExpenseFilter` y `PaymentFilter` (django-filter) por `estado` y `fecha`
    - _Requirements: 9.2, 9.4, 9.6, 9.8, 9.9_
  - [ ]* 18.3 Property test: Property 26 (serializer de gastos expone monto pendiente)
    - En `api/tests/test_api.py`, generar un gasto con historial de pagos arbitrario y comprobar que `ExpenseSerializer(gasto).data['monto_pendiente']` coincide con `gasto.monto_pendiente`, y que todos los demás campos del modelo están presentes
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 26: El serializer de gastos expone el monto pendiente correctamente`
    - **Validates: Requirements 9.2, 9.3**
  - [ ]* 18.4 Property test: Property 27 (serializer de pagos fiel al modelo)
    - Generar un pago arbitrario y comprobar que todos los campos del modelo están presentes en `PaymentSerializer(pago).data` con valores idénticos
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 27: El serializer de pagos expone todos los campos fielmente`
    - **Validates: Requirements 9.4, 9.5**
  - [ ]* 18.5 Property test: Property 28 (serializer de cuentas fiel al modelo)
    - Generar una cuenta bancaria arbitraria y comprobar que todos los campos del modelo están presentes en `BankAccountSerializer(cuenta).data` con valores idénticos
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 28: El serializer de cuentas bancarias expone todos los campos fielmente`
    - **Validates: Requirements 9.6**
  - [x] 18.6 Implementar `api/views.py`
    - `ExpenseViewSet`, `PaymentViewSet`, `BankAccountViewSet` como `ReadOnlyModelViewSet` con `filterset_class` correspondiente
    - `dashboard_summary(request)` como `APIView`/función que reutiliza `dashboard.services.get_summary()`
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  - [ ]* 18.7 Property test: Property 29 (filtrado devuelve coincidencias exactas)
    - Usando `APIClient` autenticado, generar datos con `estado`/`fecha` arbitrarios y comprobar que al filtrar por un valor, todos los elementos devueltos tienen ese valor exacto y ninguno con otro valor aparece
    - `@settings(max_examples=100)`
    - Comentario: `# Feature: expense-payment-manager, Property 29: El filtrado por campo devuelve únicamente coincidencias exactas`
    - **Validates: Requirements 9.8, 9.9**
  - [x] 18.8 Configurar `api/urls.py` con `DefaultRouter` y enlazarlo en `config/urls.py` bajo `api/`
    - _Requirements: 9.2, 9.4, 9.6, 9.7_
  - [ ]* 18.9 Escribir unit tests de autenticación de la API
    - Comprobar que una solicitud sin credenciales a cualquier endpoint devuelve `401` en formato JSON
    - _Requirements: 9.1, 9.10_

- [ ] 19. Checkpoint - Ensure all tests pass, ask the user if questions arise.

- [x] 20. Registrar las entidades en el Django admin
  - [x] 20.1 Configurar `accounts/admin.py`, `expenses/admin.py`, `payments/admin.py`
    - Registrar `BankAccount`, `Expense` y `Payment` con `list_display` (campos clave), `list_filter` (por estado) y `search_fields` (por título/referencia/nombre)
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 21. Crear datos semilla para la demo
  - [x] 21.1 Crear el comando de gestión `expenses/management/commands/seed_data.py`
    - Crear (si no existen) 2-3 usuarios, 3 `BankAccount` con saldos variados, 6-8 `Expense` cubriendo los cuatro estados, y varios `Payment` en distintos estados asociados a esos gastos, respetando las reglas de negocio (usar las funciones de `services.py`, no crear objetos "a mano" que violen invariantes)
    - Hacer el comando idempotente: si ya existen datos semilla (marcarlos con un prefijo o flag), no duplicar al re-ejecutar
    - _Requirements: 2.8, 4.10, 7.6_

- [x] 22. Documentar la API REST
  - [x] 22.1 Crear `README.md` en la raíz del proyecto
    - Documentar cómo levantar el proyecto localmente (entorno virtual, variables de entorno, migraciones, `seed_data`, usuario admin)
    - Documentar cada endpoint de la API (`/api/expenses/`, `/api/payments/`, `/api/bank-accounts/`, `/api/dashboard/summary/`): método, autenticación requerida (HTTP Basic), parámetros de filtro (`estado`, `fecha`) y un ejemplo de respuesta JSON para cada uno
    - Añadir docstrings claros en `api/views.py` y `api/serializers.py` que coincidan con lo documentado en el README
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 9.10_

- [x] 23. Preparar los archivos de configuración para despliegue en Render
  - [x] 23.1 Crear `Procfile`
    - `release: python manage.py migrate && python manage.py create_default_admin`
    - `web: gunicorn config.wsgi --log-file -`
    - _Requirements: 10.8_
  - [x] 23.2 Crear `build.sh`
    - Script que instala dependencias (`pip install -r requirements.txt`) y ejecuta `collectstatic --noinput`
    - _Requirements: 10.6_
  - [x] 23.3 Configurar Whitenoise en `config/settings.py`
    - Agregar `whitenoise.middleware.WhiteNoiseMiddleware` justo después de `SecurityMiddleware`, configurar `STATIC_ROOT` y `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
    - _Requirements: 10.6_
  - [x] 23.4 Configurar `dj-database-url` en `config/settings.py`
    - Cuando `DJANGO_ENV == 'production'`, sobrescribir `DATABASES['default']` con `dj_database_url.config(default=config('DATABASE_URL'))`
    - _Requirements: 10.8_
  - [x] 23.5 Actualizar `requirements.txt` con las dependencias finales de despliegue
    - Confirmar que `gunicorn`, `whitenoise`, `dj-database-url` y `psycopg2-binary` están pinneados a versiones exactas
    - _Requirements: 10.6_
  - [x] 23.6 Documentar en `README.md` y `.env.example` las variables de entorno requeridas para Render
    - `DJANGO_ENV=production`, `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_EMAIL`, `DJANGO_ADMIN_PASSWORD`
    - _Requirements: 1.5, 10.8_

- [ ] 24. Checkpoint final - Ensure all tests pass, ask the user if questions arise.

## Notes

- Las tareas marcadas con `*` son opcionales de saltar para un MVP más rápido, pero cubren las 29 correctness properties del diseño y deben implementarse para el examen/entrega final.
- Cada property test usa Hypothesis con `@settings(max_examples=100)` como mínimo, tal como exige el diseño.
- Los checkpoints (tareas 3, 7, 12, 15, 17, 19, 24) son puntos de control: correr toda la suite de tests (`pytest`) antes de continuar a la siguiente fase.
- Ninguna tarea ejecuta un despliegue real; las tareas 23.x solo preparan los archivos de configuración que el usuario subirá manualmente a Render.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "1.4"] },
    { "id": 3, "tasks": ["1.5"] },
    { "id": 4, "tasks": ["2.1", "2.2", "2.3"] },
    { "id": 5, "tasks": ["2.4"] },
    { "id": 6, "tasks": ["2.5"] },
    { "id": 7, "tasks": ["2.6"] },
    { "id": 8, "tasks": ["2.7"] },
    { "id": 9, "tasks": ["4.1", "5.1", "6.1"] },
    { "id": 10, "tasks": ["4.2", "5.2", "6.2"] },
    { "id": 11, "tasks": ["4.3", "5.3", "6.3"] },
    { "id": 12, "tasks": ["5.4", "6.4"] },
    { "id": 13, "tasks": ["5.5", "6.5"] },
    { "id": 14, "tasks": ["5.6", "6.6"] },
    { "id": 15, "tasks": ["6.7"] },
    { "id": 16, "tasks": ["6.8"] },
    { "id": 17, "tasks": ["6.9"] },
    { "id": 18, "tasks": ["6.10"] },
    { "id": 19, "tasks": ["6.11"] },
    { "id": 20, "tasks": ["6.12"] },
    { "id": 21, "tasks": ["6.13"] },
    { "id": 22, "tasks": ["8.1", "9.1", "10.1"] },
    { "id": 23, "tasks": ["8.2", "9.2", "10.2"] },
    { "id": 24, "tasks": ["8.3", "9.5", "10.4"] },
    { "id": 25, "tasks": ["8.4", "9.6", "10.6"] },
    { "id": 26, "tasks": ["8.5", "9.3", "10.7"] },
    { "id": 27, "tasks": ["9.4", "10.3"] },
    { "id": 28, "tasks": ["9.7", "10.5"] },
    { "id": 29, "tasks": ["10.8"] },
    { "id": 30, "tasks": ["11.1"] },
    { "id": 31, "tasks": ["11.2"] },
    { "id": 32, "tasks": ["11.3"] },
    { "id": 33, "tasks": ["13.1"] },
    { "id": 34, "tasks": ["13.2"] },
    { "id": 35, "tasks": ["13.3"] },
    { "id": 36, "tasks": ["14.1", "14.2", "14.3"] },
    { "id": 37, "tasks": ["16.1"] },
    { "id": 38, "tasks": ["16.2", "16.3"] },
    { "id": 39, "tasks": ["16.4", "16.5"] },
    { "id": 40, "tasks": ["16.6", "16.7"] },
    { "id": 41, "tasks": ["16.8", "16.9"] },
    { "id": 42, "tasks": ["16.10"] },
    { "id": 43, "tasks": ["18.1"] },
    { "id": 44, "tasks": ["18.2"] },
    { "id": 45, "tasks": ["18.3"] },
    { "id": 46, "tasks": ["18.4"] },
    { "id": 47, "tasks": ["18.5"] },
    { "id": 48, "tasks": ["18.6"] },
    { "id": 49, "tasks": ["18.7"] },
    { "id": 50, "tasks": ["18.8"] },
    { "id": 51, "tasks": ["18.9"] },
    { "id": 52, "tasks": ["20.1"] },
    { "id": 53, "tasks": ["21.1"] },
    { "id": 54, "tasks": ["22.1"] },
    { "id": 55, "tasks": ["23.1", "23.2", "23.3"] },
    { "id": 56, "tasks": ["23.4"] },
    { "id": 57, "tasks": ["23.5"] },
    { "id": 58, "tasks": ["23.6"] }
  ]
}
```
