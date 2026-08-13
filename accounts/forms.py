from django import forms

from accounts.models import BankAccount


class BankAccountForm(forms.ModelForm):
    """ModelForm para BankAccount.

    El campo ``saldo_actual`` solo se muestra al crear una cuenta nueva (con un
    valor inicial permitido). Al editar una cuenta existente, el campo se
    excluye por completo del formulario para que nunca pueda modificarse vía
    este formulario: el saldo solo cambia mediante los servicios de pagos.
    """

    class Meta:
        model = BankAccount
        fields = [
            "nombre",
            "banco",
            "numero_cuenta",
            "saldo_actual",
            "moneda",
            "activa",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si la instancia ya existe en base de datos (edición), se elimina el
        # campo saldo_actual del formulario para que jamás pueda modificarse.
        if self.instance and self.instance.pk:
            self.fields.pop("saldo_actual", None)
