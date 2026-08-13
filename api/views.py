"""Vistas de la API REST (Django REST Framework).

Todos los endpoints son de solo lectura (`ReadOnlyModelViewSet`) y requieren
autenticación HTTP Basic (configurado globalmente en
`REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`). Una solicitud sin
credenciales válidas recibe una respuesta HTTP 401 con un mensaje de error
en formato JSON. Ver Requisito 9 y el README.md del proyecto (sección
"Documentación de la API REST") para el detalle completo con ejemplos de
respuesta.

Endpoints expuestos (registrados en `api/urls.py`):
- GET /api/expenses/            -> lista de gastos (filtrable por estado, fecha)
- GET /api/expenses/{id}/       -> detalle de un gasto (incluye monto_pendiente)
- GET /api/payments/            -> lista de pagos (filtrable por estado, fecha)
- GET /api/payments/{id}/       -> detalle de un pago
- GET /api/bank-accounts/       -> lista de cuentas bancarias
- GET /api/bank-accounts/{id}/  -> detalle de una cuenta bancaria
- GET /api/dashboard/summary/   -> resumen financiero agregado
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from accounts.models import BankAccount
from dashboard.services import get_summary
from expenses.models import Expense
from payments.models import Payment

from .filters import ExpenseFilter, PaymentFilter
from .serializers import BankAccountSerializer, ExpenseSerializer, PaymentSerializer


class ExpenseViewSet(ReadOnlyModelViewSet):
    """`GET /api/expenses/` y `GET /api/expenses/{id}/`.

    Requiere autenticación HTTP Basic. Devuelve todos los campos de
    `Expense` más el campo calculado `monto_pendiente` (ver
    `ExpenseSerializer`).

    Soporta filtrado por `estado` (coincidencia exacta con
    `BORRADOR`/`APROBADO`/`PAGADO`/`CANCELADO`) y `fecha` (fecha exacta,
    formato `YYYY-MM-DD`) vía query params
    (p. ej. `/api/expenses/?estado=APROBADO&fecha=2024-01-01`).
    """

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filterset_class = ExpenseFilter


class PaymentViewSet(ReadOnlyModelViewSet):
    """`GET /api/payments/` y `GET /api/payments/{id}/`.

    Requiere autenticación HTTP Basic. Devuelve todos los campos de
    `Payment`.

    Soporta filtrado por `estado` (coincidencia exacta con
    `PENDIENTE`/`APROBADO`/`EFECTUADO`/`CANCELADO`) y `fecha` (fecha
    exacta, formato `YYYY-MM-DD`) vía query params.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter


class BankAccountViewSet(ReadOnlyModelViewSet):
    """`GET /api/bank-accounts/` y `GET /api/bank-accounts/{id}/`.

    Requiere autenticación HTTP Basic. Devuelve todos los campos de
    `BankAccount`. No soporta filtros por `estado`/`fecha`.
    """

    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


@api_view(["GET"])
def dashboard_summary(request):
    """`GET /api/dashboard/summary/`.

    Requiere autenticación HTTP Basic. Reutiliza
    `dashboard.services.get_summary()` para devolver `total_gastos`,
    `total_pagado`, `total_pendiente` y `saldo_total_activo` en formato
    JSON.
    """
    return Response(get_summary())
