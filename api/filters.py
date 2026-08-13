"""Filtros de django-filter para los endpoints de la API.

`ExpenseFilter` y `PaymentFilter` permiten filtrar por `estado` (coincidencia
exacta) y `fecha` (fecha exacta) vía query params, según el Requisito 9.8/9.9.
"""

import django_filters

from expenses.models import Expense
from payments.models import Payment


class ExpenseFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(choices=Expense.Estado.choices)
    fecha = django_filters.DateFilter(field_name="fecha")

    class Meta:
        model = Expense
        fields = ["estado", "fecha"]


class PaymentFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(choices=Payment.Estado.choices)
    fecha = django_filters.DateFilter(field_name="fecha")

    class Meta:
        model = Payment
        fields = ["estado", "fecha"]
