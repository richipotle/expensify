from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from expenses import services
from expenses.forms import ExpenseForm
from expenses.models import Expense


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = "expenses/expense_list.html"
    context_object_name = "gastos"


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = "expenses/expense_detail.html"
    context_object_name = "gasto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gasto = self.object
        context["monto_pendiente"] = gasto.monto_pendiente
        context["pagos"] = gasto.pagos.all()
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("expenses:detail", kwargs={"pk": self.object.pk})


class ExpenseEditableRequiredMixin:
    """Restringe la edición/eliminación a gastos en estado BORRADOR."""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado != Expense.Estado.BORRADOR:
            messages.error(
                request,
                "Solo los gastos en estado BORRADOR pueden editarse o eliminarse.",
            )
            return redirect("expenses:detail", pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)


class ExpenseUpdateView(LoginRequiredMixin, ExpenseEditableRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"

    def get_success_url(self):
        return reverse_lazy("expenses:detail", kwargs={"pk": self.object.pk})


class ExpenseDeleteView(LoginRequiredMixin, ExpenseEditableRequiredMixin, DeleteView):
    model = Expense
    template_name = "expenses/expense_confirm_delete.html"
    success_url = reverse_lazy("expenses:list")


@login_required
@require_POST
def expense_approve(request, pk):
    gasto = get_object_or_404(Expense, pk=pk)
    try:
        services.aprobar_gasto(gasto, request.user)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("expenses:detail", pk=pk)

    messages.success(request, "Gasto aprobado correctamente.")
    return redirect("expenses:detail", pk=pk)


@login_required
@require_POST
def expense_cancel(request, pk):
    gasto = get_object_or_404(Expense, pk=pk)
    try:
        services.cancelar_gasto(gasto, request.user)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("expenses:detail", pk=pk)

    messages.success(request, "Gasto cancelado correctamente.")
    return redirect("expenses:detail", pk=pk)


@login_required
def expense_generate_payment(request, pk):
    gasto = get_object_or_404(Expense, pk=pk)
    if gasto.estado != Expense.Estado.APROBADO:
        messages.error(
            request,
            "Solo se puede generar un pago para un gasto en estado APROBADO.",
        )
        return redirect("expenses:detail", pk=pk)

    return redirect(f"{reverse_lazy('payments:create')}?expense_id={pk}")
