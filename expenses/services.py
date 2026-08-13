from django.core.exceptions import ValidationError

from .models import Expense


def aprobar_gasto(gasto, user):
    """Aprueba un gasto.

    Solo transiciona el estado BORRADOR -> APROBADO. Para cualquier otro
    estado inicial, lanza ValidationError sin modificar el gasto.
    """
    if gasto.estado != Expense.Estado.BORRADOR:
        raise ValidationError(
            f"No se puede aprobar un gasto en estado {gasto.get_estado_display()}. "
            "Solo los gastos en BORRADOR pueden aprobarse."
        )

    gasto.estado = Expense.Estado.APROBADO
    gasto.save(update_fields=["estado", "actualizado_en"])
    return gasto


def cancelar_gasto(gasto, user):
    """Cancela un gasto.

    Solo transiciona los estados BORRADOR/APROBADO -> CANCELADO. Para
    PAGADO o CANCELADO, lanza ValidationError sin modificar el gasto.
    """
    if gasto.estado not in (Expense.Estado.BORRADOR, Expense.Estado.APROBADO):
        raise ValidationError(
            f"No se puede cancelar un gasto en estado {gasto.get_estado_display()}. "
            "Solo los gastos en BORRADOR o APROBADO pueden cancelarse."
        )

    gasto.estado = Expense.Estado.CANCELADO
    gasto.save(update_fields=["estado", "actualizado_en"])
    return gasto


def recalcular_estado_pago(gasto):
    """Recalcula el estado de un gasto en función de su monto_pendiente.

    - Si el gasto está CANCELADO, no hace nada (estado terminal).
    - Si monto_pendiente <= 0, transiciona a PAGADO.
    - Si monto_pendiente > 0 y el estado actual era PAGADO, vuelve a APROBADO.
    - En cualquier otro caso, no hace falta cambiar nada.
    """
    if gasto.estado == Expense.Estado.CANCELADO:
        return gasto

    if gasto.monto_pendiente <= 0:
        if gasto.estado != Expense.Estado.PAGADO:
            gasto.estado = Expense.Estado.PAGADO
            gasto.save(update_fields=["estado", "actualizado_en"])
    else:
        if gasto.estado == Expense.Estado.PAGADO:
            gasto.estado = Expense.Estado.APROBADO
            gasto.save(update_fields=["estado", "actualizado_en"])

    return gasto
