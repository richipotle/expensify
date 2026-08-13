"""Serializers de la API REST.

Expone los tres modelos del dominio (`BankAccount`, `Expense`, `Payment`)
con todos sus campos. `ExpenseSerializer` agrega además el campo calculado
`monto_pendiente`, que no existe como columna en base de datos sino como
`property` del modelo.
"""

from rest_framework import serializers

from accounts.models import BankAccount
from expenses.models import Expense
from payments.models import Payment


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializa todos los campos de `BankAccount`.

    Ver Requisito 9.6 y Property 28 (todos los campos del modelo deben
    estar presentes con valores idénticos a los del modelo).
    """

    class Meta:
        model = BankAccount
        fields = "__all__"


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializa `Expense` incluyendo el campo calculado `monto_pendiente`.

    Ver Requisito 9.3 y Property 26 (el campo `monto_pendiente` debe
    coincidir exactamente con la property del modelo).
    """

    monto_pendiente = serializers.ReadOnlyField()

    class Meta:
        model = Expense
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Serializa todos los campos de `Payment`.

    Ver Requisito 9.4/9.5 y Property 27 (todos los campos del modelo deben
    estar presentes con valores idénticos a los del modelo).
    """

    class Meta:
        model = Payment
        fields = "__all__"
