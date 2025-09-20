from django.urls import path
from clients.views import RegisterView, ActivateAccountView

# Ну тут просто регистрируем эндпоинты 
# Я решил не делать все в одном файле, а стараться для 
# каждого апликейшна делать отдельный url файл
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/", ActivateAccountView.as_view(), name="activate"),
]