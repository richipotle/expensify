from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("", views.BankAccountListView.as_view(), name="list"),
    path("nuevo/", views.BankAccountCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BankAccountDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.BankAccountUpdateView.as_view(), name="update"),
    path("<int:pk>/desactivar/", views.bankaccount_deactivate, name="deactivate"),
]
