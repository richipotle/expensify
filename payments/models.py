from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        EFECTUADO = "EFECTUADO", "Efectuado"
        CANCELADO = "CANCELADO", "Cancelado"

    gasto = models.ForeignKey(
        "expenses.Expense", on_delete=models.PROTECT, related_name="pagos"
    )
    cuenta_bancaria = models.ForeignKey(
        "accounts.BankAccount", on_delete=models.PROTECT, related_name="pagos"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    fecha = models.DateField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    referencia = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pagos_creados"
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pago {self.pk} - {self.gasto.titulo} ({self.get_estado_display()})"

    def clean(self):
        if self.monto is not None and self.monto <= 0:
            raise ValidationError({"monto": "El monto debe ser mayor a cero."})
