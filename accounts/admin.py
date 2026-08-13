from django.contrib import admin

from .models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("nombre", "banco", "numero_cuenta", "saldo_actual", "moneda", "activa")
    list_filter = ("activa", "moneda")
    search_fields = ("nombre", "banco", "numero_cuenta")
