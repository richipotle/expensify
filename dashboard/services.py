from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from accounts.models import BankAccount
from expenses.models import Expense
from payments.models import Payment


def get_summary():
    """Devuelve el resumen financiero para las tarjetas del dashboard.

    Retorna un dict con:
    - total_gastos: suma de monto_total de todos los gastos.
    - total_pagado: suma de monto de los pagos en estado EFECTUADO.
    - total_pendiente: suma de monto_pendiente de todos los gastos.
    - saldo_total_activo: suma de saldo_actual de las cuentas activas.
    """
    total_gastos = Expense.objects.aggregate(total=Sum("monto_total"))["total"] or Decimal("0.00")

    total_pagado = Payment.objects.filter(estado=Payment.Estado.EFECTUADO).aggregate(
        total=Sum("monto")
    )["total"] or Decimal("0.00")

    total_pendiente = sum(
        (gasto.monto_pendiente for gasto in Expense.objects.all()),
        Decimal("0.00"),
    )

    saldo_total_activo = BankAccount.objects.filter(activa=True).aggregate(
        total=Sum("saldo_actual")
    )["total"] or Decimal("0.00")

    return {
        "total_gastos": total_gastos,
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
        "saldo_total_activo": saldo_total_activo,
    }


def get_top_n(queryset, n=10):
    """Devuelve los `n` elementos más recientes de un queryset, ordenados
    por fecha descendente.
    """
    return list(queryset.order_by("-fecha")[:n])


def get_expenses_by_status():
    """Devuelve un dict {estado: count} con la cantidad de gastos por
    estado, incluyendo todos los estados posibles (con 0 si no hay gastos
    en ese estado).
    """
    conteos = {estado: 0 for estado, _ in Expense.Estado.choices}
    for fila in Expense.objects.values("estado").annotate(count=Count("id")):
        conteos[fila["estado"]] = fila["count"]
    return conteos


def get_expenses_by_category():
    """Devuelve un dict {categoria: monto_total} con la suma del monto
    total de los gastos agrupados por categoría, incluyendo todas las
    categorías posibles (con 0 si no hay gastos en esa categoría).
    """
    montos = {categoria: Decimal("0.00") for categoria, _ in Expense.Categoria.choices}
    for fila in Expense.objects.values("categoria").annotate(total=Sum("monto_total")):
        montos[fila["categoria"]] = fila["total"] or Decimal("0.00")
    return montos


def get_payments_by_month(months=6):
    """Devuelve una lista de `{mes, total}` con el monto total de pagos
    EFECTUADOS agrupados por mes, para los últimos `months` meses
    (incluyendo el mes actual), ordenados cronológicamente.
    """
    hoy = timezone.localdate()
    meses = []
    for i in range(months - 1, -1, -1):
        mes_index = hoy.month - i
        anio = hoy.year
        while mes_index <= 0:
            mes_index += 12
            anio -= 1
        meses.append((anio, mes_index))

    totales_por_mes = {(anio, mes): Decimal("0.00") for anio, mes in meses}

    fecha_inicio = timezone.datetime(meses[0][0], meses[0][1], 1).date()

    pagos_agrupados = (
        Payment.objects.filter(
            estado=Payment.Estado.EFECTUADO,
            fecha__gte=fecha_inicio,
        )
        .annotate(mes_trunc=TruncMonth("fecha"))
        .values("mes_trunc")
        .annotate(total=Sum("monto"))
    )

    for fila in pagos_agrupados:
        clave = (fila["mes_trunc"].year, fila["mes_trunc"].month)
        if clave in totales_por_mes:
            totales_por_mes[clave] = fila["total"] or Decimal("0.00")

    return [
        {"mes": f"{anio}-{mes:02d}", "total": totales_por_mes[(anio, mes)]}
        for anio, mes in meses
    ]
