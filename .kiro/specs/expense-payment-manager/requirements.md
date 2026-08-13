# Documento de Requisitos

## Introducción

Este documento describe los requisitos para **Expense Payment Manager**, una aplicación web empresarial para la gestión de gastos y pagos. La aplicación permite registrar gastos corporativos, gestionarlos a través de un flujo de aprobación, vincularlos con pagos desde cuentas bancarias y visualizar el estado financiero mediante un dashboard. Está construida sobre Django (backend) + Django REST Framework (API) + Bootstrap 5 + Chart.js (frontend), con despliegue en Render.com.

---

## Glosario

- **System**: La aplicación web Expense Payment Manager.
- **User**: Usuario autenticado con acceso al sistema.
- **Admin**: Usuario con privilegios administrativos creado por defecto.
- **Expense**: Registro de un gasto empresarial con título, descripción, monto total, categoría, fecha, estado y creador.
- **Payment**: Registro de un pago vinculado a un gasto, realizado desde una cuenta bancaria.
- **BankAccount**: Cuenta bancaria registrada con saldo disponible y estado activo/inactivo.
- **ExpenseStatus**: Enum de estados del gasto — BORRADOR, APROBADO, PAGADO, CANCELADO.
- **PaymentStatus**: Enum de estados del pago — PENDIENTE, APROBADO, EFECTUADO, CANCELADO.
- **PendingAmount**: Monto total del gasto menos la suma de pagos en estado EFECTUADO.
- **DRF**: Django REST Framework, librería para construcción de APIs REST en Django.
- **Dashboard**: Vista resumen con métricas financieras y gráficos interactivos.

---

## Requisitos

### Requisito 1: Autenticación de Usuarios

**User Story:** Como usuario, quiero iniciar y cerrar sesión de forma segura, para que solo usuarios autorizados accedan al sistema.

#### Criterios de Aceptación

1. WHEN un usuario no autenticado accede a cualquier vista del sistema, THE System SHALL redirigir al usuario a la página de login.
2. WHEN un usuario proporciona credenciales válidas en el formulario de login, THE System SHALL autenticar al usuario y redirigirlo al Dashboard.
3. WHEN un usuario proporciona credenciales inválidas en el formulario de login, THE System SHALL mostrar un mensaje de error y mantener el formulario en la página de login.
4. WHEN un usuario autenticado hace clic en el botón de logout, THE System SHALL cerrar la sesión y redirigir al usuario a la página de login.
5. THE System SHALL proveer un usuario administrador por defecto con credenciales configuradas en las variables de entorno del proyecto.

---

### Requisito 2: Gestión de Gastos (CRUD)

**User Story:** Como usuario, quiero crear, consultar, editar y eliminar gastos, para que pueda registrar y mantener actualizado el registro de gastos empresariales.

#### Criterios de Aceptación

1. WHEN un usuario autenticado envía el formulario de creación de gasto con todos los campos obligatorios válidos, THE System SHALL crear el gasto con estado inicial BORRADOR y redirigir al usuario a la vista de detalle del gasto.
2. WHEN un usuario autenticado accede a la lista de gastos, THE System SHALL mostrar todos los gastos con su título, monto total, categoría, fecha y estado con codificación de color.
3. WHEN un usuario autenticado accede al detalle de un gasto, THE System SHALL mostrar todos los campos del gasto, el historial de pagos asociados y el monto pendiente de pago.
4. WHEN un usuario autenticado envía el formulario de edición de un gasto en estado BORRADOR con datos válidos, THE System SHALL actualizar el gasto y redirigir al usuario a la vista de detalle.
5. IF un usuario intenta editar un gasto cuyo estado es APROBADO, PAGADO o CANCELADO, THEN THE System SHALL rechazar la edición y mostrar un mensaje de error indicando que solo los gastos en BORRADOR son editables.
6. WHEN un usuario autenticado elimina un gasto en estado BORRADOR, THE System SHALL eliminar el gasto permanentemente y redirigir a la lista de gastos.
7. IF un usuario intenta eliminar un gasto cuyo estado es APROBADO, PAGADO o CANCELADO, THEN THE System SHALL rechazar la eliminación y mostrar un mensaje de error.
8. THE Expense SHALL contener los campos: título (texto obligatorio), descripción (texto opcional), monto total (decimal positivo obligatorio), categoría (selección de lista predefinida obligatoria), fecha (fecha obligatoria), estado (ExpenseStatus), creado_por (FK a User asignado automáticamente).

---

### Requisito 3: Flujo de Aprobación de Gastos

**User Story:** Como usuario, quiero aprobar, cancelar y marcar como pagado un gasto, para que el ciclo de vida del gasto refleje su estado real en el proceso financiero.

#### Criterios de Aceptación

1. WHEN un usuario autenticado hace clic en el botón "Aprobar" en el detalle de un gasto, THE System SHALL verificar que el estado del gasto sea BORRADOR antes de procesar la acción.
2. WHEN el estado del gasto es BORRADOR y el usuario confirma la aprobación, THE System SHALL cambiar el estado a APROBADO y mostrar un mensaje de confirmación.
3. IF un usuario intenta aprobar un gasto cuyo estado no es BORRADOR, THEN THE System SHALL rechazar la acción y mostrar un mensaje de error descriptivo.
4. WHEN un usuario autenticado hace clic en el botón "Cancelar" en el detalle de un gasto, THE System SHALL mostrar un diálogo de confirmación antes de ejecutar la cancelación.
5. WHEN un usuario confirma la cancelación de un gasto en estado APROBADO, THE System SHALL cambiar el estado a CANCELADO.
6. IF un usuario intenta cancelar un gasto cuyo estado es PAGADO o CANCELADO, THEN THE System SHALL rechazar la acción y mostrar un mensaje de error indicando que la operación no está permitida.
7. WHEN el estado de un gasto es CANCELADO, THE System SHALL impedir cualquier cambio de estado futuro del gasto, incluyendo reactivaciones, aprobaciones o pagos.
8. WHEN la suma de los montos de los pagos en estado EFECTUADO asociados a un gasto alcanza o supera el monto total del gasto, THE System SHALL cambiar automáticamente el estado del gasto a PAGADO.

---

### Requisito 4: Gestión de Pagos (CRUD)

**User Story:** Como usuario, quiero crear, consultar, editar y eliminar pagos vinculados a gastos aprobados, para que pueda registrar los pagos parciales o totales realizados desde las cuentas bancarias.

#### Criterios de Aceptación

1. WHEN un usuario autenticado envía el formulario de creación de pago con todos los campos válidos, THE System SHALL crear el pago con estado inicial PENDIENTE y redirigir al usuario a la vista de detalle del pago.
2. IF un usuario intenta crear un pago para un gasto cuyo estado no es APROBADO, THEN THE System SHALL rechazar la operación y mostrar un mensaje de error indicando que el gasto debe estar en estado APROBADO.
3. IF un usuario intenta crear un pago cuyo monto supera el PendingAmount del gasto asociado, THEN THE System SHALL rechazar la operación y mostrar el monto máximo permitido.
4. IF un usuario intenta crear un pago cuyo monto supera el saldo disponible de la BankAccount seleccionada, THEN THE System SHALL rechazar la operación y mostrar el saldo disponible de la cuenta.
5. IF ya existe un pago con el mismo gasto, la misma BankAccount y el mismo monto en la misma fecha, THEN THE System SHALL rechazar el pago como duplicado y mostrar un mensaje de error.
6. WHEN un usuario autenticado accede a la lista de pagos, THE System SHALL mostrar todos los pagos con su referencia, gasto asociado, cuenta bancaria, monto, fecha y estado con codificación de color.
7. WHEN un usuario autenticado accede al detalle de un pago, THE System SHALL mostrar todos los campos del pago y el detalle del gasto asociado.
8. WHEN un usuario autenticado edita un pago en estado PENDIENTE con datos válidos, THE System SHALL actualizar el pago y redirigir a la vista de detalle.
9. IF un usuario intenta editar un pago cuyo estado es APROBADO, EFECTUADO o CANCELADO, THEN THE System SHALL rechazar la edición y mostrar un mensaje de error.
10. THE Payment SHALL contener los campos: gasto (FK a Expense obligatorio), cuenta_bancaria (FK a BankAccount obligatoria), monto (decimal positivo obligatorio), fecha (fecha obligatoria), estado (PaymentStatus), referencia (texto opcional), notas (texto opcional).

---

### Requisito 5: Flujo de Aprobación de Pagos

**User Story:** Como usuario, quiero aprobar, efectuar y cancelar pagos, para que el ciclo de vida del pago refleje su estado real y el saldo de las cuentas bancarias sea siempre correcto.

#### Criterios de Aceptación

1. WHEN un usuario autenticado hace clic en el botón "Aprobar" en el detalle de un pago en estado PENDIENTE, THE System SHALL cambiar el estado del pago a APROBADO y mostrar un mensaje de confirmación.
2. IF un usuario intenta aprobar un pago cuyo estado no es PENDIENTE, THEN THE System SHALL rechazar la acción y mostrar un mensaje de error.
3. WHEN un usuario autenticado hace clic en el botón "Efectuar Pago" en el detalle de un pago en estado APROBADO, THE System SHALL verificar que el saldo de la BankAccount sea mayor o igual al monto del pago antes de procesar.
4. WHEN el saldo de la BankAccount es suficiente y el usuario confirma la acción de efectuar, THE System SHALL cambiar el estado del pago a EFECTUADO y descontar el monto del saldo de la BankAccount en una operación atómica.
5. IF el saldo de la BankAccount es insuficiente al momento de efectuar el pago, THEN THE System SHALL rechazar la acción y mostrar el saldo disponible actual.
6. WHEN un usuario autenticado hace clic en el botón "Cancelar" en el detalle de un pago, THE System SHALL mostrar un diálogo de confirmación antes de ejecutar la cancelación.
7. WHEN un usuario confirma la cancelación de un pago en estado EFECTUADO, THE System SHALL cambiar el estado del pago a CANCELADO y devolver el monto al saldo de la BankAccount en una operación atómica.
8. WHEN un usuario confirma la cancelación de un pago en estado PENDIENTE o APROBADO, THE System SHALL cambiar el estado del pago a CANCELADO sin modificar el saldo de ninguna BankAccount.
9. WHEN el estado de un pago es EFECTUADO y se cancela, THE System SHALL reevaluar si el gasto asociado debe volver al estado APROBADO según el PendingAmount resultante.

---

### Requisito 6: Generación Automática de Pago desde Gasto

**User Story:** Como usuario, quiero generar un pago directamente desde el detalle de un gasto aprobado, para que no tenga que ingresar manualmente los datos del gasto en el formulario de pago.

#### Criterios de Aceptación

1. WHILE el estado del gasto es APROBADO, THE System SHALL mostrar el botón "Generar Pago" en la vista de detalle del gasto.
2. WHEN un usuario hace clic en "Generar Pago" desde el detalle de un gasto APROBADO, THE System SHALL redirigir al formulario de creación de pago con el campo gasto pre-llenado con el gasto actual.
3. WHEN el formulario de creación de pago es pre-llenado desde un gasto, THE System SHALL sugerir como monto inicial el PendingAmount del gasto.
4. IF el estado del gasto no es APROBADO, THEN THE System SHALL no mostrar el botón "Generar Pago" en la vista de detalle.

---

### Requisito 7: Gestión de Cuentas Bancarias (CRUD)

**User Story:** Como usuario, quiero crear, consultar, editar y desactivar cuentas bancarias, para que pueda gestionar los fondos disponibles para realizar pagos.

#### Criterios de Aceptación

1. WHEN un usuario autenticado envía el formulario de creación de BankAccount con todos los campos válidos, THE System SHALL crear la cuenta y redirigir a la lista de cuentas.
2. WHEN un usuario autenticado accede a la lista de cuentas bancarias, THE System SHALL mostrar todas las cuentas con nombre, banco, últimos 4 dígitos, saldo actual, moneda y estado activo/inactivo.
3. WHEN un usuario autenticado edita una BankAccount con datos válidos, THE System SHALL actualizar los datos de la cuenta excluyendo el saldo_actual (que se actualiza solo mediante pagos).
4. IF un usuario intenta desactivar una BankAccount que tiene pagos en estado PENDIENTE o APROBADO, THEN THE System SHALL rechazar la desactivación y mostrar el número de pagos activos asociados.
5. WHEN una BankAccount no tiene pagos en estado PENDIENTE o APROBADO, THE System SHALL permitir al usuario cambiar el campo activa a falso.
6. THE BankAccount SHALL contener los campos: nombre (texto obligatorio), banco (texto obligatorio), número de cuenta — últimos 4 dígitos (texto de 4 caracteres numéricos obligatorio), saldo_actual (decimal no negativo obligatorio), moneda (selección de lista predefinida obligatoria), activa (booleano, verdadero por defecto).

---

### Requisito 8: Dashboard

**User Story:** Como usuario, quiero ver un resumen visual del estado financiero, para que pueda tomar decisiones informadas sobre gastos y pagos de forma rápida.

#### Criterios de Aceptación

1. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar cuatro tarjetas de resumen: total de gastos registrados, total pagado (suma de pagos EFECTUADOS), total pendiente de pago y saldo total de todas las BankAccounts activas.
2. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar una tabla con los últimos 10 gastos ordenados por fecha descendente, incluyendo estado con codificación de color.
3. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar una tabla con los últimos 10 pagos ordenados por fecha descendente.
4. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar un gráfico de dona (Chart.js) con la distribución de gastos por estado (BORRADOR, APROBADO, PAGADO, CANCELADO).
5. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar un gráfico de barras (Chart.js) con la distribución del monto total de gastos agrupados por categoría.
6. WHEN un usuario autenticado accede al Dashboard, THE System SHALL mostrar un gráfico de línea (Chart.js) con el monto total de pagos EFECTUADOS agrupados por mes para los últimos 6 meses.

---

### Requisito 9: API REST (Django REST Framework)

**User Story:** Como desarrollador, quiero consumir una API REST para consultar gastos, pagos, cuentas bancarias y el resumen del dashboard, para que sistemas externos puedan integrarse con la aplicación.

#### Criterios de Aceptación

1. THE API SHALL requerir autenticación HTTP Basic en todos los endpoints antes de devolver datos.
2. WHEN una solicitud GET autenticada llega al endpoint `/api/expenses/`, THE System SHALL devolver la lista de todos los gastos en formato JSON con todos sus campos.
3. WHEN una solicitud GET autenticada llega al endpoint `/api/expenses/{id}/`, THE System SHALL devolver el detalle del gasto correspondiente en formato JSON, incluyendo el PendingAmount calculado.
4. WHEN una solicitud GET autenticada llega al endpoint `/api/payments/`, THE System SHALL devolver la lista de todos los pagos en formato JSON con todos sus campos.
5. WHEN una solicitud GET autenticada llega al endpoint `/api/payments/{id}/`, THE System SHALL devolver el detalle del pago correspondiente en formato JSON.
6. WHEN una solicitud GET autenticada llega al endpoint `/api/bank-accounts/`, THE System SHALL devolver la lista de todas las cuentas bancarias en formato JSON con todos sus campos.
7. WHEN una solicitud GET autenticada llega al endpoint `/api/dashboard/summary/`, THE System SHALL devolver en formato JSON: total de gastos, total pagado, total pendiente y saldo total de cuentas activas.
8. WHERE el parámetro de filtro `estado` está presente en la solicitud, THE System SHALL filtrar los resultados de la lista por el valor del estado proporcionado.
9. WHERE el parámetro de filtro `fecha` está presente en la solicitud, THE System SHALL filtrar los resultados de la lista por la fecha exacta proporcionada.
10. IF una solicitud llega a cualquier endpoint de la API sin credenciales válidas, THEN THE System SHALL devolver una respuesta HTTP 401 con un mensaje de error en formato JSON.

---

### Requisito 10: Estructura del Proyecto Django

**User Story:** Como desarrollador, quiero que el proyecto esté organizado en apps Django bien separadas por dominio, para que el código sea mantenible, legible y escalable.

#### Criterios de Aceptación

1. THE System SHALL organizar la lógica de gastos en una app Django denominada `expenses`, conteniendo modelos, vistas, formularios, URLs y templates propios.
2. THE System SHALL organizar la lógica de pagos en una app Django denominada `payments`, conteniendo modelos, vistas, formularios, URLs y templates propios.
3. THE System SHALL organizar la lógica de cuentas bancarias en una app Django denominada `accounts`, conteniendo modelos, vistas, formularios, URLs y templates propios.
4. THE System SHALL organizar todos los endpoints DRF en una app Django denominada `api`, conteniendo serializers, views y URLs propios.
5. THE System SHALL proveer templates HTML con herencia de un archivo `base.html` que incluya la barra de navegación Bootstrap 5 y los bloques de contenido y scripts.
6. THE System SHALL proveer un archivo `requirements.txt` en la raíz del proyecto con versiones exactas pinneadas de todas las dependencias, incluyendo Django, djangorestframework, psycopg2-binary, gunicorn y whitenoise.
7. WHEN el entorno de ejecución es desarrollo, THE System SHALL utilizar SQLite como motor de base de datos.
8. WHEN el entorno de ejecución es producción (variable de entorno `DJANGO_ENV=production`), THE System SHALL utilizar PostgreSQL como motor de base de datos con la cadena de conexión provista en `DATABASE_URL`.
