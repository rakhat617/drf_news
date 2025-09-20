from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from clients.serializers import RegisterSerializer, ActivateAccountSerializer

# Простейшая вьюшка для регистрации 
# Решил использовать обычный АПИвью, ибо нам тут только 1 метод нужен
class RegisterView(APIView):
    permission_classes = [AllowAny]

    # Сваггеры вот эти мне все ГПТшка писала, ибо мне лень ) 
    # Я просто подправлял как мне нужно
    @swagger_auto_schema(
        operation_summary="Зарегистрироваться",
        operation_description="Регистрация нового пользователя",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Пользователь успешно создан",
                examples={
                    "application/json": {
                        "detail": "Пользователь создан. Проверьте почту для активации."
                    }
                },
            ),
            400: "Ошибка валидации"
        },
        tags=["Регистрация"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Пользователь создан. Проверьте почту для активации."},
            status=status.HTTP_201_CREATED
        )

# Простейшая вьюшка для актиации 
# Тоже использую обычный АПИвью, ибо нам тут тоже только 1 метод нужен
class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Активировать аккаунт",
        operation_description="Активация аккаунта по email и коду",
        request_body=ActivateAccountSerializer,
        responses={
            200: openapi.Response(
                description="Успешная активация",
                examples={
                    "application/json": {
                        "detail": "Аккаунт успешно активирован"
                    }
                },
            ),
            400: "Неверный код активации или ошибка валидации"
        },
        tags=["Регистрация"]
    )
    def post(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Аккаунт успешно активирован"}, status=status.HTTP_200_OK)
