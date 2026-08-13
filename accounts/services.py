from django.core.exceptions import ValidationError

from payments.models import Payment


def desactivar_cuenta(cuenta):
    """Desactiva una cuenta bancaria.

    Verifica que no existan pagos en estado PENDIENTE o APROBADO asociados
    a la cuenta antes de desactivarla. Si existen, lanza ValidationError.
    """
    pagos_activos = cuenta.pagos.filter(
        estado__in=[Payment.Estado.PENDIENTE, Payment.Estado.APROBADO]
    ).count()

    if pagos_activos > 0:
        raise ValidationError(
            f"No se puede desactivar la cuenta: tiene {pagos_activos} pago(s) activo(s)."
        )

    cuenta.activa = False
    cuenta.save(update_fields=["activa", "actualizado_en"])
    return cuenta
