from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class Expense(models.Model):
    class Categoria(models.TextChoices):
        VIATICOS = "VIATICOS", "Viáticos"
        SUMINISTROS = "SUMINISTROS", "Suministros"
        SERVICIOS = "SERVICIOS", "Servicios"
        NOMINA = "NOMINA", "Nómina"
        MARKETING = "MARKETING", "Marketing"
        OTROS = "OTROS", "Otros"

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        APROBADO = "APROBADO", "Aprobado"
        PAGADO = "PAGADO", "Pagado"
        CANCELADO = "CANCELADO", "Cancelado"

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    monto_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    fecha = models.DateField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.BORRADOR
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="gastos_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"

    @property
    def monto_pendiente(self) -> Decimal:
        """monto_total menos la suma de pagos EFECTUADOS asociados."""
        from payments.models import Payment

        pagado = self.pagos.filter(estado=Payment.Estado.EFECTUADO).aggregate(
            total=Sum("monto")
        )["total"] or Decimal("0.00")
        return self.monto_total - pagado

    def clean(self):
        if self.pk:
            estado_previo = (
                Expense.objects.filter(pk=self.pk)
                .values_list("estado", flat=True)
                .first()
            )
            if estado_previo == self.Estado.CANCELADO and self.estado != self.Estado.CANCELADO:
                raise ValidationError("Un gasto CANCELADO no puede cambiar de estado.")
