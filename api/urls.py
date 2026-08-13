from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BankAccountViewSet, ExpenseViewSet, PaymentViewSet, dashboard_summary

router = DefaultRouter()
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("payments", PaymentViewSet, basename="payment")
router.register("bank-accounts", BankAccountViewSet, basename="bankaccount")

urlpatterns = [
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path("", include(router.urls)),
]
