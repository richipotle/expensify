from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class BankAccount(models.Model):
    class Moneda(models.TextChoices):
        USD = "USD", "Dólares"
        MXN = "MXN", "Pesos Mexicanos"
        EUR = "EUR", "Euros"

    nombre = models.CharField(max_length=100)
    banco = models.CharField(max_length=100)
    numero_cuenta = models.CharField(
        max_length=4,
        validators=[RegexValidator(r"^\d{4}$", "Deben ser 4 dígitos numéricos.")],
        help_text="Últimos 4 dígitos de la cuenta.",
    )
    saldo_actual = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.USD)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.banco} ****{self.numero_cuenta})"

    def clean(self):
        if self.saldo_actual is not None and self.saldo_actual < 0:
            raise ValidationError({"saldo_actual": "El saldo no puede ser negativo."})
