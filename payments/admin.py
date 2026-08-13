from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("referencia", "gasto", "cuenta_bancaria", "monto", "fecha", "estado")
    list_filter = ("estado",)
    search_fields = ("referencia", "gasto__titulo", "cuenta_bancaria__nombre")
