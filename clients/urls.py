from django.urls import path
from clients.views import RegisterView, ActivateAccountView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/", ActivateAccountView.as_view(), name="activate"),
]