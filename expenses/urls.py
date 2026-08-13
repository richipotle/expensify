from django.urls import path

from expenses import views

app_name = "expenses"

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="list"),
    path("nuevo/", views.ExpenseCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ExpenseDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.ExpenseUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.ExpenseDeleteView.as_view(), name="delete"),
    path("<int:pk>/aprobar/", views.expense_approve, name="approve"),
    path("<int:pk>/cancelar/", views.expense_cancel, name="cancel"),
    path(
        "<int:pk>/generar-pago/",
        views.expense_generate_payment,
        name="generate_payment",
    ),
]
