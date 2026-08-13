from django.core.exceptions import ValidationError
from django.db import transaction

from expenses.models import Expense
from expenses.services import recalcular_estado_pago

from .models import Payment


def crear_pago(gasto, cuenta, monto, fecha, referencia, notas, user):
    """Crea un pago para un gasto.

    Valida, en orden:
    1. El gasto debe estar en estado APROBADO.
    2. El monto no puede superar el monto_pendiente del gasto.
    3. El monto no puede superar el saldo_actual de la cuenta bancaria.
    4. No puede existir ya un pago duplicado (mismo gasto, cuenta, monto y fecha).

    Si todas las validaciones pasan, crea el Payment en estado PENDIENTE.
    """
    if gasto.estado != Expense.Estado.APROBADO:
        raise ValidationError(
            f"No se puede crear un pago para un gasto en estado "
            f"{gasto.get_estado_display()}. El gasto debe estar APROBADO."
        )

    if monto > gasto.monto_pendiente:
        raise ValidationError(
            f"El monto del pago ({monto}) supera el monto pendiente del gasto "
            f"({gasto.monto_pendiente})."
        )

    if monto > cuenta.saldo_actual:
        raise ValidationError(
            f"El monto del pago ({monto}) supera el saldo disponible de la cuenta "
            f"({cuenta.saldo_actual})."
        )

    duplicado = Payment.objects.filter(
        gasto=gasto,
        cuenta_bancaria=cuenta,
        monto=monto,
        fecha=fecha,
    ).exists()
    if duplicado:
        raise ValidationError(
            "Ya existe un pago con el mismo gasto, cuenta, monto y fecha."
        )

    pago = Payment.objects.create(
        gasto=gasto,
        cuenta_bancaria=cuenta,
        monto=monto,
        fecha=fecha,
        referencia=referencia,
        notas=notas,
        estado=Payment.Estado.PENDIENTE,
        creado_por=user,
    )
    return pago


def aprobar_pago(payment):
    """Aprueba un pago.

    Solo transiciona el estado PENDIENTE -> APROBADO. Para cualquier otro
    estado inicial, lanza ValidationError sin modificar el pago.
    """
    if payment.estado != Payment.Estado.PENDIENTE:
        raise ValidationError(
            f"No se puede aprobar un pago en estado {payment.get_estado_display()}. "
            "Solo los pagos en PENDIENTE pueden aprobarse."
        )

    payment.estado = Payment.Estado.APROBADO
    payment.save(update_fields=["estado", "actualizado_en"])
    return payment


def efectuar_pago(payment):
    """Efectúa un pago, descontando el saldo de la cuenta bancaria.

    Valida que la cuenta bancaria tenga saldo suficiente para cubrir el
    monto del pago. Si no hay saldo suficiente, lanza ValidationError sin
    modificar el pago ni la cuenta.

    Si hay saldo suficiente, descuenta el monto del saldo de la cuenta,
    transiciona el pago a EFECTUADO y recalcula el estado del gasto
    asociado.
    """
    with transaction.atomic():
        cuenta = payment.cuenta_bancaria

        if cuenta.saldo_actual < payment.monto:
            raise ValidationError(
                f"Saldo insuficiente en la cuenta bancaria. Saldo disponible: "
                f"{cuenta.saldo_actual}."
            )

        cuenta.saldo_actual -= payment.monto
        cuenta.save(update_fields=["saldo_actual", "actualizado_en"])

        payment.estado = Payment.Estado.EFECTUADO
        payment.save(update_fields=["estado", "actualizado_en"])

        recalcular_estado_pago(payment.gasto)

    return payment


def cancelar_pago(payment):
    """Cancela un pago.

    - Si el pago está EFECTUADO: restaura el saldo de la cuenta bancaria
      (suma el monto del pago), transiciona el pago a CANCELADO y
      recalcula el estado del gasto asociado.
    - Si el pago está PENDIENTE o APROBADO: solo transiciona el pago a
      CANCELADO, sin tocar saldos de cuentas.
    - Para cualquier otro estado (por ejemplo, ya CANCELADO), lanza
      ValidationError sin modificar el pago.
    """
    with transaction.atomic():
        if payment.estado == Payment.Estado.EFECTUADO:
            cuenta = payment.cuenta_bancaria
            cuenta.saldo_actual += payment.monto
            cuenta.save(update_fields=["saldo_actual", "actualizado_en"])

            payment.estado = Payment.Estado.CANCELADO
            payment.save(update_fields=["estado", "actualizado_en"])

            recalcular_estado_pago(payment.gasto)
        elif payment.estado in (Payment.Estado.PENDIENTE, Payment.Estado.APROBADO):
            payment.estado = Payment.Estado.CANCELADO
            payment.save(update_fields=["estado", "actualizado_en"])
        else:
            raise ValidationError(
                f"No se puede cancelar un pago en estado {payment.get_estado_display()}. "
                "Un pago ya CANCELADO no puede cancelarse nuevamente."
            )

    return payment
