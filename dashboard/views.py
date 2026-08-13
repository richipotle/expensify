import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from dashboard import services
from expenses.models import Expense
from payments.models import Payment


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resumen = services.get_summary()
        ultimos_gastos = services.get_top_n(Expense.objects.all(), n=10)
        ultimos_pagos = services.get_top_n(Payment.objects.all(), n=10)
        gastos_por_estado = services.get_expenses_by_status()
        gastos_por_categoria = services.get_expenses_by_category()
        pagos_por_mes = services.get_payments_by_month(months=6)

        context.update(
            {
                "resumen": resumen,
                "ultimos_gastos": ultimos_gastos,
                "ultimos_pagos": ultimos_pagos,
                "estado_labels_json": json.dumps(
                    [Expense.Estado(estado).label for estado in gastos_por_estado.keys()]
                ),
                "estado_data_json": json.dumps(list(gastos_por_estado.values())),
                "categoria_labels_json": json.dumps(
                    [
                        Expense.Categoria(categoria).label
                        for categoria in gastos_por_categoria.keys()
                    ]
                ),
                "categoria_data_json": json.dumps(
                    [float(monto) for monto in gastos_por_categoria.values()]
                ),
                "mes_labels_json": json.dumps([fila["mes"] for fila in pagos_por_mes]),
                "mes_data_json": json.dumps(
                    [float(fila["total"]) for fila in pagos_por_mes]
                ),
            }
        )
        return context
