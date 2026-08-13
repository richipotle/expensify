from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts import services
from accounts.forms import BankAccountForm
from accounts.models import BankAccount


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = "accounts/bankaccount_list.html"
    context_object_name = "cuentas"


class BankAccountDetailView(LoginRequiredMixin, DetailView):
    model = BankAccount
    template_name = "accounts/bankaccount_detail.html"
    context_object_name = "cuenta"


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "accounts/bankaccount_form.html"
    success_url = reverse_lazy("accounts:list")


class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "accounts/bankaccount_form.html"
    success_url = reverse_lazy("accounts:list")


@login_required
@require_POST
def bankaccount_deactivate(request, pk):
    cuenta = get_object_or_404(BankAccount, pk=pk)
    try:
        services.desactivar_cuenta(cuenta)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("accounts:detail", pk=pk)

    messages.success(request, "Cuenta desactivada correctamente.")
    return redirect("accounts:list")
