from django import forms

from expenses.models import Expense


class ExpenseForm(forms.ModelForm):
    """ModelForm para Expense.

    Solo expone los campos editables por el usuario. ``creado_por`` se
    asigna en la vista (a partir de ``request.user``) y ``estado`` se
    gestiona exclusivamente a través de la capa de servicios, nunca desde
    este formulario.
    """

    class Meta:
        model = Expense
        fields = [
            "titulo",
            "descripcion",
            "monto_total",
            "categoria",
            "fecha",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "monto_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
