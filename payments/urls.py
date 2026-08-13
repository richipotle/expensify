from django.urls import path

from payments import views

app_name = "payments"

urlpatterns = [
    path("", views.PaymentListView.as_view(), name="list"),
    path("nuevo/", views.PaymentCreateView.as_view(), name="create"),
    path("<int:pk>/", views.PaymentDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.PaymentUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.PaymentDeleteView.as_view(), name="delete"),
    path("<int:pk>/aprobar/", views.payment_approve, name="approve"),
    path("<int:pk>/efectuar/", views.payment_execute, name="execute"),
    path("<int:pk>/cancelar/", views.payment_cancel, name="cancel"),
]
