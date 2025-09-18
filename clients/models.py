import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата создания"
        )

    def __str__(self):
        return f"Activation code for {self.user.email}"
    
    class Meta:
        ordering = ("id",)
        verbose_name = "код активации"
        verbose_name_plural = "коды активации"
