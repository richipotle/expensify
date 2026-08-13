from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
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

from expenses.models import Expense
from payments import services
from payments.forms import PaymentForm
from payments.models import Payment


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "pagos"


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "payments/payment_detail.html"
    context_object_name = "pago"


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"

    def get_initial(self):
        initial = super().get_initial()
        expense_id = self.request.GET.get("expense_id")
        if expense_id:
            gasto = get_object_or_404(Expense, pk=expense_id)
            initial["gasto"] = gasto
            initial["monto"] = gasto.monto_pendiente
        return initial

    def form_valid(self, form):
        try:
            self.object = services.crear_pago(
                gasto=form.cleaned_data["gasto"],
                cuenta=form.cleaned_data["cuenta_bancaria"],
                monto=form.cleaned_data["monto"],
                fecha=form.cleaned_data["fecha"],
                referencia=form.cleaned_data["referencia"],
                notas=form.cleaned_data["notas"],
                user=self.request.user,
            )
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("payments:detail", kwargs={"pk": self.object.pk})


class PaymentEditableRequiredMixin:
    """Restringe la edición/eliminación a pagos en estado PENDIENTE."""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado != Payment.Estado.PENDIENTE:
            messages.error(
                request,
                "Solo los pagos en estado PENDIENTE pueden editarse o eliminarse.",
            )
            return redirect("payments:detail", pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)


class PaymentUpdateView(LoginRequiredMixin, PaymentEditableRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"

    def get_success_url(self):
        return reverse_lazy("payments:detail", kwargs={"pk": self.object.pk})


class PaymentDeleteView(LoginRequiredMixin, PaymentEditableRequiredMixin, DeleteView):
    model = Payment
    template_name = "payments/payment_confirm_delete.html"
    success_url = reverse_lazy("payments:list")


@login_required
@require_POST
def payment_approve(request, pk):
    pago = get_object_or_404(Payment, pk=pk)
    try:
        services.aprobar_pago(pago)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("payments:detail", pk=pk)

    messages.success(request, "Pago aprobado correctamente.")
    return redirect("payments:detail", pk=pk)


@login_required
@require_POST
def payment_execute(request, pk):
    pago = get_object_or_404(Payment, pk=pk)
    try:
        services.efectuar_pago(pago)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("payments:detail", pk=pk)

    messages.success(request, "Pago efectuado correctamente.")
    return redirect("payments:detail", pk=pk)


@login_required
@require_POST
def payment_cancel(request, pk):
    pago = get_object_or_404(Payment, pk=pk)
    try:
        services.cancelar_pago(pago)
    except ValidationError as e:
        messages.error(request, " ".join(e.messages))
        return redirect("payments:detail", pk=pk)

    messages.success(request, "Pago cancelado correctamente.")
    return redirect("payments:detail", pk=pk)
