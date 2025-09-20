from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Client, ActivationCode

# Сигнал, который сработает после регистрации 
# а именно после сохранения нового инстанса модели Client
@receiver(post_save, sender=Client)
def create_activation_code(sender, instance, created, **kwargs):
    # тут вот проверка чтоб он был неактивным
    # ибо например суперюзер создается уже активным
    if created and not instance.is_active:
        # создаем, собственно, код активации
        ActivationCode.objects.create(client=instance) 

        # и отправляем его в логи
        # я вот на самом деле забыл как это по настоящему делается
        # чтобы через почту на почту отправлялось и тд
        send_mail(
            subject="Активация аккаунта",
            message=f"Ваш код активации: {instance.activation_code.code}",
            from_email="noreply@example.com",
            recipient_list=[instance.email],
        )