from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Client, ActivationCode
import uuid


@receiver(post_save, sender=Client)
def create_activation_code(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        ActivationCode.objects.create(client=instance)

        # отправляем письмо (пока через консоль)
        send_mail(
            subject="Активация аккаунта",
            message=f"Ваш код активации: {instance.activation_code.code}",
            from_email="noreply@example.com",
            recipient_list=[instance.email],
        )