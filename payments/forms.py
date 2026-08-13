from django import forms

from payments.models import Payment


class PaymentForm(forms.ModelForm):
    """ModelForm para Payment.

    ``creado_por`` se asigna en la vista (a partir de ``request.user``) y
    ``estado`` se gestiona exclusivamente a través de la capa de servicios,
    nunca desde este formulario.
    """

    class Meta:
        model = Payment
        fields = [
            "gasto",
            "cuenta_bancaria",
            "monto",
            "fecha",
            "referencia",
            "notas",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }
