import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

# Это класс для управления созданием наших кастомных юзеров, так называемых клиентов
# Я особо тут не парился, просто по минимуму сделал
class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# Это уже сама кастомная модель юзера
# Тут я тоже особо ниче не делал, ибо по заданию нам только имейл нужен
# И нужно использовать имейл для авторизации
# Поэтому я и сделал его как юзернейм филд
class Client(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name="эл. почта",
    )
    
    is_active = models.BooleanField(
        default=False,
        verbose_name="активен/нет",
        )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="админ/нет",
        )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата регистрации",
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = ClientManager()

    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ("id",)
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


# Можно было не делать эту модель, а просто сделать поле в модели юзера
# Но я решил, что более умно сделать именно так
# Чтобы например можно было добавить сюда еще поля всякие, например срок действия и т.д
# Или например чтобы можно было их легко удалять после активации 
# (что я и реализовал здесь, хотя не уверен хорошо это или плохо)
class ActivationCode(models.Model):
    client = models.OneToOneField(
        to=Client, 
        on_delete=models.CASCADE, 
        related_name="activation_code",
        verbose_name="пользователь"
        )
    code = models.CharField(
        max_length=64, 
        unique=True, 
        default=uuid.uuid4,
        verbose_name="код активации",
        )

    def __str__(self):
        return f"Activation code for {self.user.email}"
    
    class Meta:
        ordering = ("id",)
        verbose_name = "код активации"
        verbose_name_plural = "коды активации"
