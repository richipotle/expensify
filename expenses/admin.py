from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("titulo", "monto_total", "categoria", "fecha", "estado", "creado_por")
    list_filter = ("estado", "categoria")
    search_fields = ("titulo", "descripcion")
